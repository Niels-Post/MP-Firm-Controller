import time
from typing import NewType, Optional, Callable, Any, List

from warehouse_pmsv_tracker.robot import Robot
from warehouse_pmsv_tracker.robot.command import Command, ReturnCode, Response

from warehouse_pmsv_tracker.util.shape import Pose



TestScenarioFinished = NewType('TestScenarioFinished', Optional[Callable[[Any], None]])


class TestScenario:
    """
    TestScenario can be extended to implement various kinds of testscenarios.

    TestScenario keeps information about all commands sent and responses received within it, and also tracks
    the selected robot's position throughout the scenario.
    """

    def __init__(self, robot: Robot, test_steps: List[Command], finish_callback: Optional[TestScenarioFinished] = None):
        """
        Create a testscenario
        :param robot: Robot to perform the test on
        :param test_steps: A list of commands to execute sequentially
        :param finish_callback: Method to be called when the complete scenario finishes or an error occurs
        """
        self.success = False
        self.finished = False
        self.robot_id = robot.id
        self._robot = robot
        self.current_step = 0
        self.current_step_start_time = 0
        self.percent_complete = 0
        self.finish_callback = finish_callback
        self.result = None
        self.test_steps = [{
            "command": step,
            "responses": [],
            "pose_before": Pose((0, 0), 0),
            "pose_after": Pose((0, 0), 0),
            "elapsed_time": 0.0
        } for step in test_steps]

    def _finalize_test_result(self) -> None:
        """
        Finalize_test_result should be implemented to interpret test data.
        The method is automatically called when the scenario finishes successfully, and should set self.result.

        Self.result is automatically added to the test status route.
        """
        pass

    @classmethod
    def get_test_description(cls) -> dict:
        """
        Return a dictionary containing information about the test.
        Use the format described in the superclass
        :return:
        """
        return {
            "description": "This test scenario does not have a description yey",
            "results": {
            },
            "prerequisites": "Please add a description by implementing get_test_description"
        }

    def _on_finished(self):
        self._finalize_test_result()
        self.finished = True
        self.success = True
        if self.finish_callback is not None:
            self.finish_callback(self)

    def _on_error_occured(self, message_id):
        self.finished = True
        self.finish_callback(self)

    def _on_step_update(self, response: Response):
        self.test_steps[self.current_step]['responses'].append(response)

        if response.return_code == ReturnCode.ACTION_STARTED:
            return

        if response.return_code != ReturnCode.SUCCESS:
            return self._on_error_occured(response.message_id)

        self.test_steps[self.current_step]['elapsed_time'] = time.time() - self.current_step_start_time
        self.test_steps[self.current_step]['pose_after'] = self._robot.current_pose
        self._start_next_step()

    def _start_next_step(self):
        self.current_step += 1
        self.percent_complete = self.current_step / len(self.test_steps) * 100
        if self.current_step >= len(self.test_steps):
            self._on_finished()
            return

        self._send_current_command()

    def _send_current_command(self):
        self.current_step_start_time = time.time()
        self.test_steps[self.current_step]['pose_before'] = self._robot.current_pose
        self._robot.send_command(
            self.test_steps[self.current_step]['command'],
            self._on_step_update,
            self._on_error_occured
        )

    def run(self):
        """
        Start running the test scenario.
        This method can be called multiple times to run the scenario multiple times.
        Results will be reset each time
        :return:
        """
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
