from typing import List, Union, Tuple, Callable, NewType

import cv2
import numpy as np

from warehouse_pmsv_tracker.detection.aruco import Aruco
from warehouse_pmsv_tracker.detection.calibration.CameraUndistortion import CameraUndistortion
from warehouse_pmsv_tracker.detection.transformation import PositionTransformer
from warehouse_pmsv_tracker.detection.aruco import ArucoSquare, ArucoID
from warehouse_pmsv_tracker.detection.transformation.shape import Quadrilateral, Rectangle, Pose


PoseListener = NewType('PoseListener', Callable[[Pose],None])

class PositionDetectionPipeline:
    """The Position Detection Pipeline combines all functionality to detect a robots' position"""

    def __init__(self,
                 camera_undistortion_calibration_file: str,
                 capture_device: cv2.VideoCapture):
        self.capture_device: cv2.VideoCapture = capture_device
        self.camera_undistortion: CameraUndistortion = CameraUndistortion(camera_undistortion_calibration_file)
        self.aruco_detection: Aruco = Aruco()
        self.position_transformer: Union[PositionTransformer, None] = None

        self.pose_listeners: List[Tuple[ArucoID, PoseListener]] = []

    def setup_area(self, corner_markers: ArucoSquare, real_area_size: Rectangle, num_retries: int = 50) -> Quadrilateral:
        for _ in range(num_retries):
            success, original_image = self.capture_device.read()
            image = self.camera_undistortion.undistort(original_image)

            if not success: continue

            detection_result = self.aruco_detection.process(image)
            area = detection_result.get_four_marker_quadrilateral(corner_markers)

            if area is not None:
                break
        else:
            raise Exception("Cannot find area in camera image")
        self.position_transformer = PositionTransformer(area, real_area_size)

        return area


    def add_pose_listener(self, aruco_id: ArucoID, listener: PoseListener):
        self.pose_listeners.append((aruco_id, listener))

    def remove_pose_listeners_for_id(self, aruco_id: ArucoID):
        for current_listener in (listener for listener in self.pose_listeners if listener[0] == aruco_id):
            self.pose_listeners.remove(current_listener)

    def remove_pose_listener(self, aruco_id: ArucoID, listener: PoseListener):
        self.pose_listeners.remove((aruco_id, listener))

    def find_markers(self, markers: List[ArucoID]) -> Tuple[np.ndarray, List[Quadrilateral], List[Quadrilateral]]:
        ret, original_image = self.capture_device.read()
        if not ret:
            raise Exception("Error capturing image from video source")

        undistorted_image = self.camera_undistortion.undistort(original_image, True)

        aruco_detection_result = self.aruco_detection.process(undistorted_image)

        marker_quadrilaterals = aruco_detection_result.get(markers)

        transformed_marker_quadrilaterals = None

        if self.position_transformer is not None:
            transformed_marker_quadrilaterals = [self.position_transformer.get_transformed_quad(quad) if quad.is_valid() else quad for quad in
                                     marker_quadrilaterals]

        return undistorted_image, marker_quadrilaterals, transformed_marker_quadrilaterals
