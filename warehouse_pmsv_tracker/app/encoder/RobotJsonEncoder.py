from enum import Enum

from flask.json import JSONEncoder

from warehouse_pmsv_tracker.detection.transformation.shape.Pose import Pose
from warehouse_pmsv_tracker.robot import Robot
from warehouse_pmsv_tracker.robot.command.Command import Command
from warehouse_pmsv_tracker.robot.command.Response import Response
from warehouse_pmsv_tracker.robot.testing.TestScenario import TestScenario


class RobotJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Robot):
            return {
                "id": o.id,
                "current_pose": o.current_pose,
                "current_state": o.current_state
            }

        if isinstance(o, Command):
            return {
                "category_id": o.category_id,
                "command_id": o.command_id,
                "parameters": o.parameters,
                "message_id": o.message_id,
            }

        if isinstance(o, Response):
            return {
                "message_id": o.message_id,
                "return_code": o.return_code,
                "data": o.data
            }

        if isinstance(o, TestScenario):
            return {
                "success": o.success,
                "finished": o.finished,
                "test_steps": o.test_steps,
                "robot_id": o.robot_id,
                "percent_complete": o.percent_complete,
                "result": o.result
            }

        if isinstance(o, Pose):
            return {
                "position": o.position,
                "angle": o.angle
            }

        if isinstance(o, Enum):
            return o.name

        return JSONEncoder.default(self, o)
