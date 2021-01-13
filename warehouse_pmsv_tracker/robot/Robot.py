from enum import IntEnum
from typing import Optional, Union

from warehouse_pmsv_tracker.detection import ArucoDetectionPipeline
from warehouse_pmsv_tracker.detection.aruco import ArucoID
from warehouse_pmsv_tracker.robot import MultiRobotConnection, CommandCallback, ErrorCallback
from warehouse_pmsv_tracker.robot.command import Response, Command, ReturnCode
from warehouse_pmsv_tracker.robot.command.factory import ActionCommandFactory
from warehouse_pmsv_tracker.robot.command.registry import Category
from warehouse_pmsv_tracker.util.shape import Pose, Point


class RobotState(IntEnum):
    """
    Enum indicating the connection state of a connected robot
    """
    IDLE = 0
    COMMAND_SENT = 1
    WORKING = 2
    ERROR_OCCURED = 3
    DISCONNECTED = 4


def _logged_command(cmd: Command):
    return {
        "message_id": cmd.message_id,
        "category": Category(cmd.category_id).name,
        "text": cmd.__repr__(),
        "type": "command"
    }


def _logged_response(resp: Response):
    return {
        "message_id": resp.message_id,
        "category": resp.return_code.name,
        "text": resp.__repr__(),
        "type": "response"
    }


class Robot:
    def __init__(self, id: ArucoID, multi_robot_connection: MultiRobotConnection,
                 detection_pipeline: Optional[ArucoDetectionPipeline]):
        """
        Initialize (connect to) a robot
        :param id: ID of the robot
        :param multi_robot_connection: Multi robot connection to attach the robot to
        :param detection_pipeline: Detection pipeline to use for position tracking
        """
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
        """
        Destructor to remove attachment to the detection pipeline and the multirobot connection
        :return:
        """
        if self.pipeline is not None:
            self.pipeline.remove_pose_listener(self.id, self._set_pose)
        if self.multi_robot_connection is not None:
            self.multi_robot_connection.unregister_robot(self.id)

    def send_command(self, command: Command, response_callback: Optional[CommandCallback] = None,
                     error_callback: ErrorCallback = None, log = True):
        """
        Send a command to the robot
        :param command: Command to sent
        :param response_callback: Function to be called when any response is received (may be called multiple times)
        :param error_callback: Function to be called when an error occurs in transmission
        :return:
        """
        self.current_state = RobotState.COMMAND_SENT

        def on_response(response: Response):
            if log:
                self.logged_messages.append(_logged_response(response))
            if response.return_code == ReturnCode.SUCCESS:
                self.current_state = RobotState.IDLE
            elif response.return_code == ReturnCode.ACTION_STARTED:
                self.current_state = RobotState.WORKING
            else:
                self.current_state = RobotState.ERROR_OCCURED

            if response_callback is not None:
                response_callback(response)

        def on_error(message_id):
            self.current_state = RobotState.DISCONNECTED
            if error_callback is not None:
                error_callback(message_id)

        self.multi_robot_connection.send_command(
            self.id,
            command,
            on_response,
            on_error
        )
        if log:
            self.logged_messages.append(_logged_command(command))

    def _set_pose(self, new_pose: Pose):
        self.current_pose = new_pose

    def _assert_connection(self):
        if self.multi_robot_connection is None or not self.multi_robot_connection.is_registered(self.id):
            raise Exception("Robot does not seem to be connected/registered")

    def move_mm(self, mm: int, direction: Union[bool, None]):
        """
        Move the robot by a specified distance
        :param mm:
        :param direction:
        :return:
        """
        cmd = ActionCommandFactory.start_move_mm(mm, direction)
        self.send_command(cmd)

    def rotate_degrees(self, deg: int, direction: bool):
        """
        Rotate the robot a specified number of degrees
        :param deg:
        :param direction:
        :return:
        """
        cmd = ActionCommandFactory.start_rotate_degrees(deg, direction)
        self.send_command(cmd)
