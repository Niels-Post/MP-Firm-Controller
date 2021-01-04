from warehouse_pmsv_tracker.detection.ArucoDetectionPipeline import ArucoDetectionPipeline
from warehouse_pmsv_tracker.detection.aruco import ArucoID
from warehouse_pmsv_tracker.detection.transformation.shape import Pose, Point
from warehouse_pmsv_tracker.robot.MultiRobotConnection import MultiRobotConnection
from warehouse_pmsv_tracker.robot.category.ActionCommand import ActionCommand


class Robot:
    def __init__(self, id: ArucoID, multi_robot_connection: MultiRobotConnection):
        self.id = id
        self.current_pose: Pose = Pose(Point((0., 0.)), 0)
        self.pipeline: ArucoDetectionPipeline = None
        self.multi_robot_connection = multi_robot_connection
        pass

    def __del__(self):
        if self.pipeline is not None:
            self.pipeline.remove_pose_listener(self.id, self._set_pose)

    def _set_pose(self, new_pose: Pose):
        self.current_pose = new_pose

    def attach_to_detection_pipeline(self, pipeline: ArucoDetectionPipeline):
        self.pipeline = pipeline
        self.pipeline.add_pose_listener(self.id, self._set_pose)

    def move_to_position(self, position: Point):
        # self.multi_robot_connection.send_command(self.id, ActionCommand.cancel_movement())
        pass

    def print(self):
        print("Robot[id:{},position:{},angle:{}]".format(self.id, self.current_pose.position, self.current_pose.angle))




