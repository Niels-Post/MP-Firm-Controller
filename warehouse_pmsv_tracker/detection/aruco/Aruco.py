import os
from itertools import product
from typing import Union, List, Iterable, NewType, Collection

import cv2
import numpy as np
from cv2 import aruco

from warehouse_pmsv_tracker.detection.transformation.shape import Quadrilateral

# Type to represent Aruco IDs
ArucoID = NewType('ArucoID', int)

# Type to represent a square of ArucoIDs (topleft, topright, bottomleft, bottomright
ArucoSquare = NewType('ArucoSquare', Collection[ArucoID])


class ArucoDetectionResult:
    """
    A datatype containing information about a set of detected aruco markers
    """

    def __init__(self, corners, ids: np.ndarray):
        self.corners = corners
        self.ids = ids

    def get(self, markers: Union[ArucoID, Iterable[ArucoID]]) -> Union[List[Quadrilateral], Quadrilateral]:
        """
        Retrieve the bounds of one or more markers

        Note that when not found, a marker is returned as a zero-quadrilateral (0,0,0,0)
        When multiple markers are requested, a list is returned. When only one is requested, it is returned as a single Quadrilateral
        :param markers: IDs of the markers to retrieve, or (in case of one marker) a single ID
        :return:
        """
        if isinstance(markers, list):
            return [self.get(marker) for marker in markers]

        return Quadrilateral(*self.corners[np.where(self.ids == markers)[0][0]][0][[0,1,3,2]]) if np.any(
            self.ids == markers) else Quadrilateral(*[(0,0)] * 4)

    def get_four_marker_quadrilateral(self, square: ArucoSquare) -> Union[Quadrilateral, None]:
        """"
            Find a quadrilateral consisting of 4 aruco markers.

            This method finds the outer corners of the 4 markers and returns a new quadrilateral of those corners
        """
        if not all(np.isin(square, self.ids)): return None

        bools = sorted(product([False, True], [True, False]), key=lambda x: x[1])

        outer_corners = [
            self.get(square).find_outer_corner(*bool_tup) for bool_tup, square in zip(bools, square)
        ]

        return Quadrilateral(*outer_corners)

    def draw(self, image: np.ndarray):
        """
        Draw the detected markers onto an image
        :param image: Image to draw on
        :return:  None
        """
        aruco.drawDetectedMarkers(image, self.corners, self.ids)


class Aruco:

    def __init__(self, aruco_dict_id=aruco.DICT_ARUCO_ORIGINAL):
        self.aruco_dict = aruco.Dictionary_get(aruco_dict_id)
        self.parameters = aruco.DetectorParameters_create()

    def process(self, image) -> ArucoDetectionResult:
        """
        Find all aruco markers in an image.

        :return: An ArucoDetectionResult containing all found markers
        """

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        corners, ids, _ = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)
        return ArucoDetectionResult(corners, ids)

    @classmethod
    def generate_marker_pairs(cls, amount: int, output_directory: str, aruco_dict_id=aruco.DICT_ARUCO_ORIGINAL,
                              x_offset=20, y_offset=20, marker_size=500):
        """
        Generate markers for printing

        :param amount: How many markers to create
        :param output_directory: Output directory to put markers in
        :param aruco_dict_id: Which Aruco Dictionary to print markers for
        :param x_offset: Horizontal offset from the page edge for each markerea
        :param y_offset: Vertical offset from the page edge for each marker
        :param marker_size: Size of each marker in pixels
        :return:
        """
        aruco_dict = aruco.Dictionary_get(aruco_dict_id)

        for i in range(0, amount, 2):
            marker_1 = aruco.drawMarker(aruco_dict, i, marker_size)
            marker_2 = aruco.drawMarker(aruco_dict, i + 1, marker_size)

            markers_a4 = np.zeros([marker_size * 2 + y_offset * 4, marker_size + x_offset * 2], dtype=np.uint8)
            markers_a4.fill(255)

            markers_a4[y_offset:y_offset + marker_size, x_offset:x_offset + marker_size] = marker_1
            markers_a4[y_offset * 3 + marker_size:y_offset * 3 + marker_size * 2,
            x_offset:x_offset + marker_size] = marker_2

            cv2.imwrite(os.path.join(output_directory, "aruco_%i_%i.jpg") % (i - 1, i), markers_a4)
