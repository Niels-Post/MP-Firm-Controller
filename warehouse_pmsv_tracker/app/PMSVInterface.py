# from flask import Flask, json
# from warehouse_pmsv_tracker.robot.MultiRobotConnection import MultiRobotConnection
#
# api = Flask(__name__)
#
# robotConnections = MultiRobotConnection()
#
#
#
# @api.route('/robots', methods=['GET'])
# def get_robots():
#     pass
#
# api.run()
from warehouse_pmsv_tracker.detection.transformation.shape.Rectangle import Rectangle

from warehouse_pmsv_tracker.warehouse.WarehousePMSV import WarehousePMSV

if __name__ == '__main__':
    test = WarehousePMSV((4,0,1,5), Rectangle(0,0,1000,500))

    while True:
        test.update()
        [robot.print() for robot in test.robots]