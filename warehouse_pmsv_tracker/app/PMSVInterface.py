import logging
import os
import time
from multiprocessing.context import Process

import requests
from flask import Flask

from warehouse_pmsv_tracker.app.encoder.RobotJsonEncoder import RobotJsonEncoder
from warehouse_pmsv_tracker.app.route.camfeed import construct_camfeed_blueprint
from warehouse_pmsv_tracker.app.route.robot import construct_robot_blueprint
from warehouse_pmsv_tracker.app.route.scenario import construct_scenario_blueprint
from warehouse_pmsv_tracker.detection.aruco import ArucoQuad
from warehouse_pmsv_tracker.detection.transformation.shape import Rectangle
from warehouse_pmsv_tracker.warehouse import WarehousePMSV

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def api_task():
    api = Flask(__name__, static_folder=os.path.dirname(__file__) + "/html", static_url_path="")
    api.json_encoder = RobotJsonEncoder

    test = WarehousePMSV(
        ArucoQuad(4, 0, 1, 5),
        Rectangle(0, 0, 1200, 650)
    )
    api.register_blueprint(construct_camfeed_blueprint(test), url_prefix='/webcam')
    api.register_blueprint(construct_robot_blueprint(test), url_prefix="/robot")
    api.register_blueprint(construct_scenario_blueprint(test), url_prefix="/scenario")

    @api.route("/")
    def root():
        return api.send_static_file("index.html")

    @api.route('/update', methods=['GET'])
    def update():
        test.update()
        return "{success: true}"

    api.run("0.0.0.0")



def update_task():
    while True:
        requests.get("http://127.0.0.1:5000/update")


if __name__ == '__main__':
    api_process = Process(target=api_task)
    api_process.start()

    time.sleep(1)

    # update_process = Process(target=update_task)
    # update_process.start()

    api_process.join()
    # update_process.join()
