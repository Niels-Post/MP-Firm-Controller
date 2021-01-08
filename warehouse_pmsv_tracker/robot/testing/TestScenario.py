from typing import List, Callable, Any, Optional, NewType

from warehouse_pmsv_tracker.detection.transformation.shape.Pose import Pose
from warehouse_pmsv_tracker.robot import Robot
from warehouse_pmsv_tracker.robot.MultiRobotConnection import MultiRobotConnection
from warehouse_pmsv_tracker.robot.command import Response
from warehouse_pmsv_tracker.robot.command.Command import Command
from warehouse_pmsv_tracker.robot.command.Response import ReturnCode

TestScenarioFinished = NewType('TestScenarioFinished', Optional[Callable[[Any], None]])


class TestScenario:
    def __init__(self, robot: Robot, test_steps: List[Command], finish_callback: TestScenarioFinished):
        self.success = False
        self.finished = False
        self.robot_id = robot.id
        self._robot = robot
        self.current_step = 0
        self.percent_complete = 0
        self.finish_callback = finish_callback
        self.result = None
        self.test_steps = [{
            "command": step,
            "responses": [],
            "pose_before": Pose((0, 0), 0),
            "pose_after": Pose((0, 0), 0)
        } for step in test_steps]

    def _finalize_test_result(self):
        pass

    @classmethod
    def get_test_description(cls) -> dict:
        raise NotImplementedError()

    def _on_finished(self):
        self._finalize_test_result()
        self.finished = True
        self.success = True
        self.finish_callback(self)

    def _on_error_occured(self):
        self.finished = True
        self.finish_callback(self)

    def _on_step_update(self, response: Response):
        self.test_steps[self.current_step]['responses'].append(response)

        if response.return_code == ReturnCode.ACTION_STARTED:
            return

        if response.return_code != ReturnCode.SUCCESS:
            return self._on_error_occured()

        self.test_steps[self.current_step]['pose_after'] = self._robot.current_pose
        self.start_next_step()

    def start_next_step(self):
        self.current_step += 1
        self.percent_complete = self.current_step / len(self.test_steps) * 100
        if self.current_step >= len(self.test_steps):
            self._on_finished()
            return

        self._send_current_command()

    def _send_current_command(self):
        self.test_steps[self.current_step]['pose_before'] = self._robot.current_pose
        self._robot.send_command(
            self.test_steps[self.current_step]['command'],
            self._on_step_update,
            self._on_error_occured
        )

    def run(self):
        self.success = False
        self.percent_complete = 0
        self.test_steps = [{
            "command": step['command'],
            "responses": [],
            "pose_before": Pose((0, 0), 0),
            "pose_after": Pose((0, 0), 0)
        } for step in self.test_steps]
        self.current_step = 0
        self._send_current_command()
