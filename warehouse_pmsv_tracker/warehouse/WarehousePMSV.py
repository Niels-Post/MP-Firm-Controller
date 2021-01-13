from typing import Dict

import cv2

from warehouse_pmsv_tracker.detection import ArucoDetectionPipeline
from warehouse_pmsv_tracker.detection.aruco import ArucoQuad, ArucoID
from warehouse_pmsv_tracker.robot import MultiRobotConnection, Robot
from warehouse_pmsv_tracker.robot.command.factory import GeneralCommandFactory
from warehouse_pmsv_tracker.util.shape import Rectangle


class WarehousePMSV:
    def __init__(self, testarea_corners: ArucoQuad, real_testarea_size: Rectangle):
        """
        Create the Warehouse PMSV.

        Fails if the area cannot be found on the cameraview
        :param testarea_corners: Corners of the test area
        :param real_testarea_size: The actual size of the test area in millimeters
        """
        self.detection_pipeline = ArucoDetectionPipeline(
            cv2.VideoCapture(0),
            "../../resources/cybertrack_h3_calibration.yaml",
            testarea_corners,
            real_testarea_size,
            self.on_new_marker_detected
        )
        self.robotConnection = MultiRobotConnection()
        self.robots: Dict[int, Robot] = dict()

    def robot_added(self, id):
        """
        Called when a robot successfully responds to a SET_ID command
        :param id: Id that the robot responded for
        :return:
        """
        robot = Robot(id, self.robotConnection, self.detection_pipeline)
        self.robots[id] = robot

    def on_new_marker_detected(self, id: ArucoID):
        """
        Called when a new marker is detected.

        Attempts to connect to the corresponding robot by sending a SET_ID command with the detected id
        :param id: ID that was detected
        :return:
        """
        self.robotConnection.broadcast_command(GeneralCommandFactory.set_id(id),
                                               lambda msg: self.robot_added(id),
                                               lambda msg_id: self.detection_pipeline.untrack(id))

    def update(self):
        """
        Checks for incoming messages, and for updates in the position of the aruco_markers markers
        :return:
        """
        self.detection_pipeline.process_next_frame()
        self.robotConnection.process_incoming_data()
