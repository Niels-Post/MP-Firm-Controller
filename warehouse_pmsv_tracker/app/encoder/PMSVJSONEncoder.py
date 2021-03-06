#
# Copyright (c) 2021. Niels Post. AI Lab Vrije Universiteit Brussel.
#
# This file is part of MP-Firm.
#
# MP-Firm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MP-Firm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MP-Firm.  If not, see <https://www.gnu.org/licenses/>.
#


from typing import Any

from flask.json import JSONEncoder
from enum import Enum

from warehouse_pmsv_tracker.app.route.ConfigurationBluePrint import ConfigValueInformation
from warehouse_pmsv_tracker.robot import Robot
from warehouse_pmsv_tracker.robot.command import Command, Response

from warehouse_pmsv_tracker.robot.testing import TestScenario
from warehouse_pmsv_tracker.util.shape import Pose


class PMSVJSONEncoder(JSONEncoder):
    """
        Encodes JSON objects for transfer to the web client.

        Currently adds JSON serialization for:
        - Robot
        - Command
        - Response
        - TestScenario
        - Pose
        - Enum (python's default one)
    """
    def default(self, o: Any):
        if isinstance(o, Robot):
            return {
                "id": o.id,
                "current_pose": o.current_pose,
                "current_state": o.current_state.name
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

        if isinstance(o, ConfigValueInformation):
            return {
                "name": o.name,
                "type": o.type,
                "id": o.id,
                "value": o.value
            }

        if isinstance(o, Enum):
            return o.name

        return JSONEncoder.default(self, o)
