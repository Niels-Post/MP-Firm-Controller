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

"""
Main Interface for the PMSV application.

This application exposes a webinterface through which robots can be controlled in a warehouse environment.

Test Setup
===========

Robots
---------

All robots are moving platform robots running MP-Firm. Instructions on how to build the robots, and how to install MP-Firm can be found
HERE https://www.instructables.com/Building-a-Moving-Platform-Robot-From-Scratch/.
After setting up, each robot needs to have a unique aruco_markers code stuck on top. These are used to identify robots, and
later send directed commands to them.

NOTE: Make sure each robot is running the same version of MP-firm to prevent unexpected behaviour.

Warehouse Environment
------------------------

Mount a webcam connected to the raspberry pi to the ceiling, with a view plane as perpendicular to the ground as possible.

Mark the working area using 4 different Aruco markers. Make sure none of these match a marker that is stuck to a robot.
Make sure the working area is rectangular, then measure it.

Enter the ids of the used aruco_markers markers in the variable 'testarea_corner_markers' below, in the order:
top left, top right, bottom left, bottom right

Input the width and height in mm (relative to the camera's view) into the variable 'testarea_dimensions' below.


Starting Up
--------------

Make sure no robots are in camera view yet.

Run the Application.

Use a webbrowser to visit: <PI_IP>:5000. A web page should pop up with the camera live view.

Now connect each robot using the following steps:

- Turn on the robot
- Wait for the robot to show its id on the display, make sure this matches the number of the code stuck on top
- Introduce the robot into camera view
- The Application should automatically connect to the robot
- After connecting, the webpage should show the robot's number in the robot list in the top right

After this, robots can be controlled through the webinterface or through the API.
"""

import logging
import os

from flask import Flask, jsonify

from warehouse_pmsv_tracker.app.encoder import PMSVJSONEncoder
from warehouse_pmsv_tracker.app.route import construct_robot_blueprint, construct_camfeed_blueprint, \
    construct_scenario_blueprint
from warehouse_pmsv_tracker.app.route.ConfigurationBluePrint import construct_configuration_blueprint
from warehouse_pmsv_tracker.detection.aruco import ArucoQuad
from warehouse_pmsv_tracker.util.shape import Rectangle
from warehouse_pmsv_tracker.warehouse import WarehousePMSV

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

testarea_corner_markers = ArucoQuad(1,4,0,5)
testarea_dimensions = Rectangle(0, 0, 1200, 650)


def start_pmsv_interface():
    pmsv_webinterface = Flask(__name__, static_folder=os.path.dirname(__file__) + "/html", static_url_path="")
    pmsv_webinterface.json_encoder = PMSVJSONEncoder


    warehouse_pmsv = WarehousePMSV(
        testarea_corner_markers,
        testarea_dimensions
    )

    pmsv_webinterface.register_blueprint(construct_camfeed_blueprint(warehouse_pmsv), url_prefix='/webcam')
    pmsv_webinterface.register_blueprint(construct_robot_blueprint(warehouse_pmsv), url_prefix="/robot")
    pmsv_webinterface.register_blueprint(construct_scenario_blueprint(warehouse_pmsv), url_prefix="/scenario")
    pmsv_webinterface.register_blueprint(construct_configuration_blueprint(warehouse_pmsv), url_prefix="/config")

    @pmsv_webinterface.route("/")
    def root():
        return pmsv_webinterface.send_static_file("index.html")


    @pmsv_webinterface.route("/is_area_detected")
    def is_area_detected():
        """
        Check if the working area was detected
        :return:
        """

        return jsonify(area_detected=warehouse_pmsv.detection_pipeline.testarea_position_transformer is not None)

    pmsv_webinterface.run("0.0.0.0")


if __name__ == '__main__':
    start_pmsv_interface()
