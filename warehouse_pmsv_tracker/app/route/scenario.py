import uuid as uuid
from flask import Blueprint, Response, make_response, json, jsonify
from warehouse_pmsv_tracker.robot.category import ActionCommand

from warehouse_pmsv_tracker.robot.testing.TestScenario import TestScenario
from warehouse_pmsv_tracker.robot.testing.scenarios.TestRobotDistancePerMotorRotation import \
    TestRobotDistancePerMotorRotation

from warehouse_pmsv_tracker.warehouse import WarehousePMSV


def construct_scenario_blueprint(pmsv: WarehousePMSV):
    scenario_blueprint = Blueprint("blueprint", __name__)

    scenarios = {}

    @scenario_blueprint.route("")
    def get_scenarios():
        return json.dumps([
            "mm_distance_per_robot_rotation_degree",
            "robot_distance_per_motor_rotation"
        ])

    @scenario_blueprint.route("/status/<uuid>")
    def get_status(uuid):
        return json.dumps(scenarios[uuid])

    @scenario_blueprint.route("/info/<id>")
    def get_scenario_info(id):
        if id == "robot_distance_per_motor_rotation":
            return jsonify(TestRobotDistancePerMotorRotation.get_test_description())

    @scenario_blueprint.route("/<id>/robot_distance_per_motor_rotation")
    def test_distance_per_motor_rotation(id):
        id = int(id)
        test_uuid = str(uuid.uuid1())
        scenarios[test_uuid] = TestRobotDistancePerMotorRotation(pmsv.robots[id], lambda x: None)
        scenarios[test_uuid].run()
        return json.dumps({
            "id": test_uuid
        })


    @scenario_blueprint.route("/<id>/mm_distance_per_robot_rotation_degree")
    def test_mm_move(id):
        id = int(id)
        test_uuid = str(uuid.uuid1())
        scenarios[test_uuid] = TestScenario(pmsv.robots[id], [
            ActionCommand.start_rotate_degrees(90, True)
        ], lambda x: None)
        scenarios[test_uuid].run()
        return json.dumps({
            "id": test_uuid
        })


    return scenario_blueprint