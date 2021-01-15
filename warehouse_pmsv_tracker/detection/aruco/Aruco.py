# Type to represent Aruco IDs
import os
from itertools import product
from typing import NewType, NamedTuple, Union, Iterable, List

import cv2
import numpy as np
from cv2 import aruco

from warehouse_pmsv_tracker.util.shape import Quadrilateral

ArucoID = NewType('ArucoID', int)


# Type to represent a square of ArucoIDs (topleft, topright, bottomleft, bottomright
class ArucoQuad(NamedTuple):
    tl: ArucoID
    tr: ArucoID
    bl: ArucoID
    br: ArucoID


class ArucoDetectionResult:
    """
    A datatype containing information about a set of detected aruco_markers markers
    """

    def __init__(self, corners: List, ids: np.ndarray):
        self.corners = corners
        self.ids = ids

    def get_all(self):
        """
        Retrieve the IDS and positions of the currently detected Aruco Markers
        :return:
        """
        return zip(self.ids, self.get(self.ids.tolist()))

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

        return Quadrilateral(*self.corners[np.where(self.ids == markers)[0][0]][0][[0, 1, 3, 2]]) if np.any(
            self.ids == markers) else Quadrilateral(*[(0, 0)] * 4)

    def get_four_marker_quadrilateral(self, quad_markers: ArucoQuad) -> Union[Quadrilateral, None]:
        """"
            Find a quadrilateral consisting of 4 aruco_markers markers.

            This method finds the outer corners of the 4 markers and returns a new quadrilateral of those corners
        """
        if not all(np.isin(quad_markers, self.ids)): return None

        bools = sorted(product([False, True], [True, False]), key=lambda x: x[1])

        outer_corners = [
            self.get(square).find_outer_corner(*bool_tup) for bool_tup, square in zip(bools, quad_markers)
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
        Find all aruco_markers markers in an image.

        :return: An ArucoDetectionResult containing all found markers
        """

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        corners, ids, _ = aruco.detectMarkers(gray, self.aruco_dict, parameters=self.parameters)
        ids = ids.flatten()
        return ArucoDetectionResult(corners, ids)

    @classmethod
    def generate_marker_pairs(cls, amount: int, output_directory: str, aruco_dict_id=aruco.DICT_ARUCO_ORIGINAL,
                              x_offset=20, y_offset=20, big=True):
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
        marker_size = 500 if big else 250
        marker_count = 2 if big else 4
        for i in range(0, amount, marker_count):
            markers = [
                aruco.drawMarker(aruco_dict, i + j, marker_size) for j in range(marker_count)
            ]

            markers_a4 = np.zeros(
                [marker_size * 2 + 4 * y_offset, marker_size * int(marker_count / 2) + x_offset * marker_count],
                dtype=np.uint8)

            markers_a4.fill(255)

            if big:
                markers_a4[y_offset:y_offset + marker_size, x_offset:x_offset + marker_size] = markers[0]
                markers_a4[y_offset * 3 + marker_size:y_offset * 3 + marker_size * 2, x_offset:x_offset + marker_size] = \
                markers[1]
                cv2.imwrite(os.path.join(output_directory, "aruco_%i_%i.jpg") % (*[id for id in range(i, i+2)],), markers_a4)


            else:
                markers_a4[y_offset:y_offset + marker_size, x_offset:x_offset + marker_size] = markers[0]
                markers_a4[y_offset:y_offset + marker_size,
                x_offset * 3 + marker_size: x_offset * 3 + marker_size * 2] = markers[1]
                markers_a4[y_offset * 3 + marker_size:y_offset * 3 + marker_size * 2, x_offset:x_offset + marker_size] = \
                markers[2]
                markers_a4[y_offset * 3 + marker_size:y_offset * 3 + marker_size * 2,
                x_offset * 3 + marker_size: x_offset * 3 + marker_size * 2] = markers[3]
                cv2.imwrite(os.path.join(output_directory, "aruco_%i_%i_%i_%i.jpg") % (*[id for id in range(i, i+4)],), markers_a4)


