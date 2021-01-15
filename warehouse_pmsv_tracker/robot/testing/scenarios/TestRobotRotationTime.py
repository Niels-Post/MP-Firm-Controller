from math import sqrt

from warehouse_pmsv_tracker.robot import Robot
from warehouse_pmsv_tracker.robot.command.factory import ActionCommandFactory
from warehouse_pmsv_tracker.robot.testing.TestScenario import TestScenario, TestScenarioFinished


class TestRobotRotationTime(TestScenario):
    """
    Test Scenario to check the average time the robot takes to make a 90 degree turn.
    """

    def __init__(self, robot: Robot, finish_callback: TestScenarioFinished, rotation: int = 90):
        """
        Initialize the TestScenario.
        """
        self.rotation = rotation
        test_steps = [
            ActionCommandFactory.start_rotate_degrees(self.rotation, True),
            ActionCommandFactory.start_rotate_degrees(self.rotation, True),
            ActionCommandFactory.start_rotate_degrees(self.rotation, True),
            ActionCommandFactory.start_rotate_degrees(self.rotation, True)
        ]
        super().__init__(robot, test_steps, finish_callback)

    def _finalize_test_result(self):
        """
        Calculates the recommended setting adjustment for mm_distance_per_robot_rotation_degree.
        Also adds some information about the traveled rotations for context
        :return:
        """
        times = [round(step['elapsed_time'],2) for step in self.test_steps]
        self.result['elapsed_times'] = times
        self.result['average_time'] = round(sum(times) / len(times),2)


    @classmethod
    def get_test_description(cls) -> dict:
        return {
            "description": "This test scenario measures the time it takes for the robot to make a 90 degree turn\n"
                            "It is used by the warehouse simulation to set up the path graph for the simulation\n"
                           "It performs a 90 degree rotation 4 times, and calculates the average elapsed time\n",
            "results": {
                "elapsed_times": "How long the robot took per rotation to perform it",
                "average_time": "The average time the robot takes to turn"
            },
            "prerequisites": "Make sure all specific motor related settings (such as steps_per_degree) are set correctly, and the robot actually turns 90 degrees when requested"
        }