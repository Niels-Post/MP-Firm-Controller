from flask import Blueprint, Response, make_response, json

from warehouse_pmsv_tracker.warehouse import WarehousePMSV


def construct_robot_blueprint(pmsv: WarehousePMSV):
    robot_blueprint = Blueprint("robot", __name__)

    @robot_blueprint.route("")
    def get_robots():
        return json.dumps([robot.toDict() for robot in pmsv.robots.values()])

    @robot_blueprint.route("/<id>/move/<mm>/<direction>")
    def move_mm(id, mm, direction):
        pmsv.robots[int(id)].move_mm(int(mm), int(direction) == 1)
        return "{success: true}"

    @robot_blueprint.route("/<id>/rotate/<deg>/<direction>")
    def rotate_deg(id, deg, direction):
        pmsv.robots[int(id)].rotate_degrees(int(deg), int(direction) == 1)
        return "{success: true}"

    @robot_blueprint.route("/<id>/newmessages")
    def get_history(id):
        data = json.dumps(pmsv.robots[int(id)].logged_messages)
        pmsv.robots[int(id)].logged_messages = []
        return data

    return robot_blueprint