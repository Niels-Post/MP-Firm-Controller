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
import sys
from math import sqrt

import flask

from warehouse_pmsv_tracker.robot import Robot
from warehouse_pmsv_tracker.robot.command.factory import ActionCommandFactory
from warehouse_pmsv_tracker.robot.testing.TestScenario import TestScenario, TestScenarioFinished


class TestRobotTimePerDistance(TestScenario):
    """
    Test Scenario to check the average time the robot takes to move a specified distance
    """

    def __init__(self, robot: Robot, finish_callback: TestScenarioFinished, **kwargs):
        """
        Initialize the TestScenario.
        """
        self.distance = kwargs.get("start_distance", 100)
        self.distances = [self.distance]
        self.precision = kwargs.get("precision", 0.01)
        self.time_goal = kwargs.get("time_goal", 2)
        self.max_tries = kwargs.get("max_tries", 10)

        self.last_direction = True

        test_steps = [
            ActionCommandFactory.start_move_mm(self.distance, True)
        ]
        super().__init__(robot, test_steps, finish_callback)

    def on_step_done(self):
        step_result = self.test_steps[self.current_step]
        distance_factor = self.time_goal / step_result["elapsed_time"]

        print("distance: " + str(self.distance) + ", factor: " + str(distance_factor) + ", time" + str(step_result['elapsed_time']))
        if(abs(1 - distance_factor) > self.precision):
            if len(self.test_steps) > self.max_tries:
                return


            self.distance *= distance_factor
            self.last_direction = not self.last_direction
            self.distances.append(self.distance)
            self.add_step(ActionCommandFactory.start_move_mm(int(self.distance), self.last_direction))


    def _finalize_test_result(self):
        """
        Calculates the average time the requested distance takes.
        Also adds some information about the traveled rotations for context
        :return:
        """
        closest_factor = 1000
        closest_idx = 0

        for i, res in enumerate(self.test_steps):
            current_time_factor = self.time_goal / res['elapsed_time']
            if abs((1 - current_time_factor)) < abs((1 - closest_factor)):
                closest_factor = current_time_factor
                closest_idx = i

        self.result = {
            "times": [round(res['elapsed_time'],2) for res in self.test_steps],
            "distances": [round(dist,2) for dist in self.distances],
            "closest_factor": round(self.test_steps[closest_idx]['elapsed_time'],2),
            "closest_distance": round(self.distances[closest_idx],2)
        }



    @classmethod
    def get_test_description(cls) -> dict:
        return {
            "description": "This test scenario measures the time it takes for the robot to move a specified distance\n"
                            "It is used by the warehouse simulation to set up the path graph for the simulation\n"
                           "It moves a specified distance 4 times, and calculates the average elapsed time\n",
            "results": {
                "elapsed_times": "How long the robot took per move to perform it",
                "average_time": "The average time the robot takes to move the specified distance"
            },
            "prerequisites": "Make sure all specific motor related settings (such as steps_per_degree) are set correctly, and the robot actually moves the specified distance"
        }

