from enum import Enum
from typing import Optional, Union

from flask.json import JSONEncoder

from warehouse_pmsv_tracker.detection.ArucoDetectionPipeline import ArucoDetectionPipeline
from warehouse_pmsv_tracker.detection.aruco import ArucoID
from warehouse_pmsv_tracker.detection.transformation.shape import Pose, Point
from warehouse_pmsv_tracker.robot.MultiRobotConnection import MultiRobotConnection, CommandCallback, ErrorCallback
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


class Robot():
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

    def send_command(self, command: Command, response_callback: Optional[CommandCallback] = None, error_callback: ErrorCallback = None):
        self.current_state = RobotState.COMMAND_SENT

        def on_response(response: Response):
            self.logged_messages.append(logged_response(response))
            if response.return_code == ReturnCode.SUCCESS:
                self.current_state = RobotState.SUCCESS
            elif response.return_code == ReturnCode.ACTION_STARTED:
                self.current_state = RobotState.WORKING
            else:
                self.current_state = RobotState.ERROR_OCCURED

            if response_callback is not None:
                response_callback(response)

        def on_error():
            self.current_state = RobotState.DISCONNECTED
            if error_callback is not None:
                error_callback()

        self.multi_robot_connection.send_command(
            self.id,
            command,
            on_response,
            on_error
        )
        self.logged_messages.append(logged_command(command))


    def _set_pose(self, new_pose: Pose):
        self.current_pose = new_pose

    def _assert_connection(self):
        if self.multi_robot_connection is None or not self.multi_robot_connection.is_registered(self.id):
            raise Exception("Robot does not seem to be connected/registered")

    def print(self):
        print("Robot[id:{},position:{},angle:{}]".format(self.id, self.current_pose.position, self.current_pose.angle))


    def move_mm(self, mm: int, direction: Union[bool, None]):
        cmd = ActionCommand.start_move_mm(mm, direction)
        self.send_command(cmd)

    def rotate_degrees(self, deg: int, direction: bool):
        cmd = ActionCommand.start_rotate_degrees(deg, direction)
        self.send_command(cmd)
