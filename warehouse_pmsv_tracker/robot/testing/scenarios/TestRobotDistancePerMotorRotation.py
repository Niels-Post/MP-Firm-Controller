from math import sqrt

from warehouse_pmsv_tracker.robot import Robot
from warehouse_pmsv_tracker.robot.command.factory import ActionCommandFactory
from warehouse_pmsv_tracker.robot.testing.TestScenario import TestScenario, TestScenarioFinished


class TestRobotDistancePerMotorRotation(TestScenario):
    """
    Test Scenario to validate the motor_rotation_degrees_per_mm_distance settings.
    See get_test_description for more information
    """

    def __init__(self, robot: Robot, finish_callback: TestScenarioFinished, distance: int = 100):
        """
        Initialize the TestScenario.
        """
        self.distance = distance
        test_steps = [
            ActionCommandFactory.start_move_mm(self.distance, True),
            ActionCommandFactory.start_move_mm(self.distance, False)
        ]
        super().__init__(robot, test_steps, finish_callback)

    def _finalize_test_result(self):
        """
        Calculates the recommended setting adjustment for motor_rotation_degrees_per_mm_distance.
        Also adds some information about the traveled distances for context
        :return:
        """
        self.result = {
            "expected_distance": self.distance
        }

        actual_distances = []
        deviations = []
        for i, cmd in enumerate(self.test_steps):
            diff = cmd['pose_after'] - cmd['pose_before']
            distance = sqrt(pow(diff.position[0], 2) + pow(diff.position[1], 2))
            actual_distances.append(round(distance, 2))
            deviations.append(round(distance - self.result['expected_distance'], 2))

        self.result['deviations'] = deviations
        self.result['actual_distances'] = actual_distances

        self.result['recommended_factor'] = round(
            self.result['expected_distance'] / (sum(actual_distances) / len(actual_distances)), 2)

    @classmethod
    def get_test_description(cls) -> dict:
        return {
            "description": "This test scenario can be used to tweak the 'motor_rotation_degrees_per_mm_distance' setting.\n"
                           "This setting decides how far (in mm) the robot moves for each degree it turns both wheels.\n\n"
                           "The test moves the robot 100 mm in both directions, and uses the camera to measure the actual outcome",
            "results": {
                "expected_distance": "The distance the robot should move in this test",
                "actual_distances": "The actual distances measured when moving the robot",
                "deviations": "The deviations of each actual distance to the expected distance",
                "recommended_factor": "The recommended factor to adjust 'motor_rotation_degrees_per_mm_distance' by"
            },
            "prerequisites": "Make sure all specific motor related settings (such as steps_per_degree) are set correctly"
        }
