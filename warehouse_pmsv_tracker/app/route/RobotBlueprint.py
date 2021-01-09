from flask import Blueprint, jsonify

from warehouse_pmsv_tracker.warehouse import WarehousePMSV

def construct_robot_blueprint(pmsv: WarehousePMSV):
    """
    Create the blueprint for the entire /robot/ route.

    This route is responsible for all immediate interactions with robots.
    Through this route, the client can view connected robots, move robots and view their status.

    :param pmsv: PMSV to connect to
    :return: Flask Blueprint for the /robot route
    """

    robot_blueprint = Blueprint("robot", __name__)

    @robot_blueprint.route("/all")
    def get_robots():
        """
        Get Pose, state and ID for all robots currently connected
        :return:
        """
        return jsonify(robots=pmsv.robots)

    @robot_blueprint.route("/<id>/move/<mm>/<direction>")
    def move_mm(id, mm, direction):
        """
        Move a robot a specified distance in a direction
        :param id: ID of the robot
        :param mm: Amount of mm to move
        :param direction:  Direction to move in (1 for forward, 0 for backward)
        :return: success:true if the robot is connected and the command was sent
        """
        if int(id) not in pmsv.robots:
            return jsonify(success=False, error="Unknown robot")

        pmsv.robots[int(id)].move_mm(int(mm), int(direction) == 1)
        return jsonify(success=True)


    @robot_blueprint.route("/<id>/rotate/<deg>/<direction>")
    def rotate_deg(id, deg, direction):
        """
        Rotate a robot a specified amount of degrees in a direction
        :param id: ID of the robot to move
        :param deg: Amount of degrees to rotate
        :param direction: Direction to rotate in (1 for right, 0 for left)
        :return: Success:true if the robot is connected and the command was sent
        """
        if int(id) not in pmsv.robots:
            return jsonify(success=False, error="Unknown robot")

        pmsv.robots[int(id)].rotate_degrees(int(deg), int(direction) == 1)
        return jsonify(success=True)

    @robot_blueprint.route("/<id>/newmessages")
    def get_history(id):
        """
        Retrieve all commands and responses sent to and received from the robot since the last time this route was
        queried for this robot
        :param id: ID Of the robot to query
        :return: Messages: a list of all messages sent to and from the robot
        """
        if int(id) not in pmsv.robots:
            return jsonify(error="Unknown robot")

        data = jsonify(messages=pmsv.robots[int(id)].logged_messages)
        pmsv.robots[int(id)].logged_messages = []
        return data

    return robot_blueprint
