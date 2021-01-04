import cv2

from warehouse_pmsv_tracker.detection.ArucoDetectionPipeline import ArucoDetectionPipeline
from warehouse_pmsv_tracker.detection.aruco import ArucoSquare, ArucoID
from warehouse_pmsv_tracker.detection.transformation.shape.Rectangle import Rectangle
from warehouse_pmsv_tracker.robot import Robot
from warehouse_pmsv_tracker.robot.MultiRobotConnection import MultiRobotConnection
from warehouse_pmsv_tracker.robot.category.GeneralCommand import GeneralCommand


class WarehousePMSV:
    def __init__(self, corner_markers: ArucoSquare, real_area_size: Rectangle):
        self.DetectionPipeline = ArucoDetectionPipeline("../../resources/cybertrack_h3_calibration.yaml",
                                                        cv2.VideoCapture(0), self.on_new_id)
        self.DetectionPipeline.setup_area(corner_markers, real_area_size)
        self.robotConnection = MultiRobotConnection()
        self.robots = []

    def robot_added(self, id):
        robot = Robot(id, self.robotConnection)
        self.robots.append(robot)
        robot.attach_to_detection_pipeline(self.DetectionPipeline)

    def on_new_id(self, id: ArucoID):
        self.robotConnection.broadcast_command(GeneralCommand.set_id(id),
                                               lambda msg: self.robot_added(id),
                                               lambda: self.DetectionPipeline.unfollow(id))

    def update(self):
        self.DetectionPipeline.update()
        self.robotConnection.process_incoming_data()
