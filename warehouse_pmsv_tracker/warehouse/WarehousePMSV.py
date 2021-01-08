from typing import Dict

import cv2

from warehouse_pmsv_tracker.detection.ArucoDetectionPipeline import ArucoDetectionPipeline
from warehouse_pmsv_tracker.detection.aruco import ArucoQuad, ArucoID
from warehouse_pmsv_tracker.detection.transformation.shape.Rectangle import Rectangle
from warehouse_pmsv_tracker.robot import Robot
from warehouse_pmsv_tracker.robot.MultiRobotConnection import MultiRobotConnection
from warehouse_pmsv_tracker.robot.category.GeneralCommand import GeneralCommand


class WarehousePMSV:
    def __init__(self, testarea_corners: ArucoQuad, real_testarea_size: Rectangle):
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
        robot = Robot(id, self.robotConnection, self.detection_pipeline)
        self.robots[id] = robot

    def on_new_marker_detected(self, id: ArucoID):
        self.robotConnection.broadcast_command(GeneralCommand.set_id(id),
                                               lambda msg: self.robot_added(id),
                                               lambda: self.detection_pipeline.untrack(id))

    def update(self):
        self.detection_pipeline.process_next_frame()
        self.robotConnection.process_incoming_data()
