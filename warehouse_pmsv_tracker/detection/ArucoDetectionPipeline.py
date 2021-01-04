from typing import List, Union, Tuple, Callable, NewType

import cv2

from warehouse_pmsv_tracker.detection.aruco import Aruco
from warehouse_pmsv_tracker.detection.aruco import ArucoSquare, ArucoID
from warehouse_pmsv_tracker.detection.calibration.CameraUndistortion import CameraUndistortion
from warehouse_pmsv_tracker.detection.transformation import PositionTransformer
from warehouse_pmsv_tracker.detection.transformation.shape import Quadrilateral, Rectangle, Pose

PoseListener = NewType('PoseListener', Callable[[Pose], None])


class ArucoDetectionPipeline:
    """The Position Detection Pipeline combines all functionality to detect a robots' position"""

    def __init__(self,
                 camera_undistortion_calibration_file: str,
                 capture_device: cv2.VideoCapture,
                 on_new_id: Callable[[ArucoID], None]):
        self.capture_device: cv2.VideoCapture = capture_device
        self.undistorted_image = None
        self.camera_undistortion: CameraUndistortion = CameraUndistortion(camera_undistortion_calibration_file)
        self.aruco_detection: Aruco = Aruco()
        self.position_transformer: Union[PositionTransformer, None] = None
        self.on_new_id = on_new_id
        self.pose_listeners: List[Tuple[ArucoID, PoseListener]] = []
        self.following: List[ArucoID] = []
        self.corner_markers = None

    def setup_area(self, corner_markers: ArucoSquare, real_area_size: Rectangle,
                   num_retries: int = 50) -> Quadrilateral:
        self.corner_markers = corner_markers
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

    def update(self):
        ret, original_image = self.capture_device.read()
        if not ret:
            raise Exception("Error capturing image from video source")

        self.undistorted_image = self.camera_undistortion.undistort(original_image, True)

        aruco_detection_result = self.aruco_detection.process(self.undistorted_image)

        for id in aruco_detection_result.ids:
            id = int(id)
            if id in self.following:
                transformed_quad = None

                for listener in self.pose_listeners:
                    if listener[0] == id:
                        if transformed_quad is None:
                            transformed_quad = aruco_detection_result.get(id)
                            if self.position_transformer is not None:
                                transformed_quad = self.position_transformer.get_transformed_quad(
                                    transformed_quad) if transformed_quad.is_valid() else transformed_quad
                        listener[1](transformed_quad.get_pose())
            elif id not in self.corner_markers:
                self.on_new_id(id)
                self.following.append(id)

    def unfollow(self, id: ArucoID):
        print("Unfollowing {}".format(id))
        if id in self.following:
            self.following.remove(id)

