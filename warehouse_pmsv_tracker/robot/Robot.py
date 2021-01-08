from enum import Enum
from typing import Optional, Union

from warehouse_pmsv_tracker.detection.ArucoDetectionPipeline import ArucoDetectionPipeline
from warehouse_pmsv_tracker.detection.aruco import ArucoID
from warehouse_pmsv_tracker.detection.transformation.shape import Pose, Point
from warehouse_pmsv_tracker.robot.MultiRobotConnection import MultiRobotConnection
from warehouse_pmsv_tracker.robot.category import ActionCommand
from warehouse_pmsv_tracker.robot.command.Command import Command, Category
from warehouse_pmsv_tracker.robot.command.Response import Response, ReturnCode


class RobotState(Enum):
    IDLE = 0
    SUCCESS = 1
    COMMAND_SENT = 2
    WORKING = 3
    ERROR_OCCURED = 4
    DISCONNECTED = 5


def logged_command(cmd: Command):
    return {
        "message_id": cmd.message_id,
        "category": Category(cmd.category_id).name,
        "text": cmd.__repr__(),
        "type": "command"
    }


def logged_response(resp: Response):
    return {
        "message_id": resp.message_id,
        "category": resp.return_code.name,
        "text": resp.__repr__(),
        "type": "response"
    }


class Robot:
    def __init__(self, id: ArucoID, multi_robot_connection: MultiRobotConnection,
                 detection_pipeline: Optional[ArucoDetectionPipeline]):
        self.id = id
        self.current_pose: Pose = Pose(Point((0., 0.)), 0)
        self.pipeline: ArucoDetectionPipeline = detection_pipeline
        self.multi_robot_connection = multi_robot_connection
        self.detection_pipeline = detection_pipeline

        self.multi_robot_connection.register_robot(id)

        self.logged_messages = []
        self.current_state: RobotState = RobotState.IDLE

        if self.detection_pipeline is not None:
            self.detection_pipeline.add_pose_listener(self.id, self._set_pose)

    def __del__(self):
        if self.pipeline is not None:
            self.pipeline.remove_pose_listener(self.id, self._set_pose)

    def _send_command(self, command: Command):
        self.current_state = RobotState.COMMAND_SENT
        self.multi_robot_connection.send_command(
            self.id,
            command,
            self._on_response_received,
            self._on_error
        )
        self.logged_messages.append(logged_command(command))

    def _on_response_received(self, response: Response):
        self.logged_messages.append(logged_response(response))
        if response.return_code == ReturnCode.SUCCESS:
            self.current_state = RobotState.SUCCESS
        elif response.return_code == ReturnCode.ACTION_STARTED:
            self.current_state = RobotState.WORKING
        else:
            self.current_state = RobotState.ERROR_OCCURED

    def _on_error(self):
        self.current_state = RobotState.DISCONNECTED

    def _set_pose(self, new_pose: Pose):
        self.current_pose = new_pose

    def _assert_connection(self):
        if self.multi_robot_connection is None or not self.multi_robot_connection.is_registered(self.id):
            raise Exception("Robot does not seem to be connected/registered")

    def print(self):
        print("Robot[id:{},position:{},angle:{}]".format(self.id, self.current_pose.position, self.current_pose.angle))

    def toDict(self):
        return {
            "id": self.id,
            "angle": self.current_pose.angle,
            "position": self.current_pose.position,
            "state": self.current_state.name
        }

    def move_mm(self, mm: int, direction: Union[bool, None]):
        cmd = ActionCommand.start_move_mm(mm, direction)
        self._send_command(cmd)

    def rotate_degrees(self, deg: int, direction: bool):
        cmd = ActionCommand.start_rotate_degrees(deg, direction)
        self._send_command(cmd)
