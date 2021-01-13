from math import sqrt

from warehouse_pmsv_tracker.robot import Robot
from warehouse_pmsv_tracker.robot.command.factory import ActionCommandFactory
from warehouse_pmsv_tracker.robot.testing.TestScenario import TestScenario, TestScenarioFinished


class TestRobotRotationPerDistance(TestScenario):
    """
    Test Scenario to validate the mm_distance_per_robot_rotation_degree.
    See get_test_description for more information
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
        self.result = {
            "expected_rotation": self.rotation
        }

        actual_distances = []
        deviations = []
        for i, cmd in enumerate(self.test_steps):
            angle_before = cmd['pose_before'].angle
            angle_after = cmd['pose_after'].angle

            if angle_after < angle_before:
                angle_after += 360

            diff = round(angle_after - angle_before,2)

            actual_distances.append(diff)

            deviations.append(round(diff - self.rotation, 2))

        self.result['deviations'] = deviations
        self.result['actual_distances'] = actual_distances

        print(deviations)
        print(actual_distances)
        self.result['recommended_factor'] = round(
            self.rotation / (sum(actual_distances) / len(actual_distances)), 2)

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
