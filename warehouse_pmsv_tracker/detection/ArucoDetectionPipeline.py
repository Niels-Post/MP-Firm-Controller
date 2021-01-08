from typing import List, Union, Tuple, Callable, NewType, Dict

import cv2

from warehouse_pmsv_tracker.detection.aruco import Aruco, ArucoQuad, ArucoID
from warehouse_pmsv_tracker.detection.calibration.CameraUndistortion import CameraUndistortion
from warehouse_pmsv_tracker.detection.transformation import PositionTransformer
from warehouse_pmsv_tracker.detection.transformation.shape import Quadrilateral, Rectangle, Pose

PoseListener = NewType('PoseListener', Callable[[Pose], None])

# Called when a new marker is found. Method should return True if the marker should be tracked, or false if not
NewMarkerListener = NewType('NewMarkerListener', Callable[[ArucoID], bool])

class ArucoDetectionPipeline:
    """
    The aruco detection pipeline takes an image from the webcam, and processes it the following way

    1. Undistort image
    2. Detect Aruco Markers
    3. Check if new markers were found
        3.1. If so, call the newMarkerListener
    4. For each found marker (except markers that are in "corner_markers")
        4.1. Transform the markers to quadriletaerals in the given real_testarea_size
        4.2. Get the pose of the transformed quads
        4.3. Call each listener associated with the id with the calculated pose
    """

    def _setup_area(self,num_retries: int = 50) -> Quadrilateral:
        self.testarea_corners = self.testarea_corners
        for _ in range(num_retries):
            success, original_image = self.capture_device.read()
            image = self.camera_undistortion.undistort(original_image)

            if not success: continue

            detection_result = self.aruco_detection.process(image)
            area = detection_result.get_four_marker_quadrilateral(self.testarea_corners)

            if area is not None:
                break
        else:
            raise Exception("Cannot find area in camera image")
        self.testarea_position_transformer = PositionTransformer(area, self.real_testarea_size)

        return area

    def __init__(self,
                 capture_device: cv2.VideoCapture,
                 camera_undistortion_file: str,
                 testarea_corners: ArucoQuad,
                 real_testarea_size: Rectangle,
                 newmarker_listener: NewMarkerListener = lambda marker: None):
        # Attributes for camera feed
        self.capture_device: cv2.VideoCapture = capture_device

        # Attributes for camera undistortion
        self.undistorted_image = None
        self.camera_undistortion: CameraUndistortion = CameraUndistortion(camera_undistortion_file)

        # Attributes for Aruco detection
        self.aruco_detection: Aruco = Aruco()
        self.newmarker_listener = newmarker_listener
        self.tracking: List[ArucoID] = []

        # Attributes for Position Transform
        self.testarea_corners = testarea_corners
        self.tracked_marker_transformed_quads = dict()
        self.real_testarea_size = real_testarea_size
        self.testarea_position_transformer: Union[PositionTransformer, None] = None
        self.pose_listeners: Dict[ArucoID, List[PoseListener]] = dict()
        self._setup_area()

    def add_pose_listener(self, aruco_id: ArucoID, listener: PoseListener):
        if aruco_id not in self.pose_listeners:
            self.pose_listeners[aruco_id] = []
        self.pose_listeners[aruco_id].append(listener)

    def remove_pose_listeners_for_id(self, aruco_id: ArucoID):
        self.pose_listeners[aruco_id] = []

    def remove_pose_listener(self, aruco_id: ArucoID, listener: PoseListener):
        if aruco_id not in self.pose_listeners:
            return
        self.pose_listeners[aruco_id] = [lstnr for lstnr in self.pose_listeners[aruco_id] if not  lstnr == listener]

    def _get_transformed_quad(self, marker_id: ArucoID, original_quad: Quadrilateral) -> Quadrilateral:
        if marker_id not in self.tracked_marker_transformed_quads:
            self.tracked_marker_transformed_quads[marker_id] = self.testarea_position_transformer.get_transformed_quad(
                original_quad) if original_quad.is_valid() else original_quad
        return self.tracked_marker_transformed_quads[marker_id]

    def process_next_frame(self):
        ret, original_image = self.capture_device.read()
        if not ret:
            raise Exception("Error capturing image from video source")

        self.tracked_marker_transformed_quads = dict()

        self.undistorted_image = self.camera_undistortion.undistort(original_image, True)

        aruco_detection_result = self.aruco_detection.process(self.undistorted_image)

        for detected_id, detected_quad in aruco_detection_result.get_all():
            detected_id = int(detected_id)
            if detected_id in self.tracking:
                if detected_id in self.pose_listeners:
                    for current_listener in self.pose_listeners[detected_id]:
                        current_listener(self._get_transformed_quad(detected_id, detected_quad).get_pose())

            elif detected_id not in self.testarea_corners:
                self.newmarker_listener(detected_id)
                self.tracking.append(detected_id)

    def untrack(self, id: ArucoID):
        if id in self.tracking:
            self.tracking.remove(id)
