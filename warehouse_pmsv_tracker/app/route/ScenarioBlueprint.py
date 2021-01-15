from typing import Dict, Type
from uuid import uuid1

from flask import Blueprint, jsonify

from warehouse_pmsv_tracker.robot.testing import TestScenario
from warehouse_pmsv_tracker.robot.testing.scenarios import TestRobotDistancePerMotorRotation, TestRobotRotationTime, \
    TestRobotRotationPerDistance
from warehouse_pmsv_tracker.warehouse import WarehousePMSV


def construct_scenario_blueprint(pmsv: WarehousePMSV):
    scenario_blueprint = Blueprint("blueprint", __name__)

    available_scenarios: Dict[str, Type[TestScenario]] = {
        "robot_distance_per_motor_rotation": TestRobotDistancePerMotorRotation,
        "robot_rotation_per_distance": TestRobotRotationPerDistance,
        "robot_rotation_time": TestRobotRotationTime
    }

    started_scenarios: Dict[str, TestScenario] = {}

    @scenario_blueprint.route("/all")
    def get_scenarios():
        """
        Get a list of the names of all available testscenarios
        :return:
        """
        return jsonify(scenarios=list(available_scenarios.keys()))

    @scenario_blueprint.route("/status/<uuid>")
    def get_status(uuid):
        """
        Get the status of a running testscenario
        :param uuid: UUID of the scenario (returned when calling /run/)
        :return:
        """
        return jsonify(started_scenarios[uuid])

    @scenario_blueprint.route("/info/<id>")
    def get_scenario_info(id):
        """
        Get all textual information about a scenario
        :param id:
        :return:
        """
        if id not in available_scenarios:
            return jsonify(error="Scenario not found")

        return jsonify(available_scenarios[id].get_test_description())

    @scenario_blueprint.route("/run/<robot_id>/<scenario_id>")
    def run_testscenario(robot_id, scenario_id):
        """
        Start running a specified testscenario on a robot
        :param robot_id: Robot to run on
        :param scenario_id: Scenario to run
        :return:
        """
        if not scenario_id in available_scenarios:
            return jsonify(error="Scenario not found")

        robot_id = int(robot_id)
        if not robot_id in pmsv.robots:
            return jsonify(error="Unknown robot")
        scenario_uuid = str(uuid1())

        started_scenarios[scenario_uuid] = available_scenarios[scenario_id](pmsv.robots[robot_id], lambda x: None)
        started_scenarios[scenario_uuid].run()
        return jsonify(uuid=scenario_uuid)

    return scenario_blueprint
