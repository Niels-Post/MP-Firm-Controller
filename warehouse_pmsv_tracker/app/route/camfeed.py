import cv2
from flask import Blueprint, Response, make_response

from warehouse_pmsv_tracker.warehouse import WarehousePMSV


def construct_camfeed_blueprint(pmsv: WarehousePMSV):
    camfeed_blueprint = Blueprint("camfeed", __name__)

    def cameragenerator():
        while True:
            pmsv.update()
            retval, buffer = cv2.imencode('.png', pmsv.detection_pipeline.undistorted_image)
            yield (b'--frame\r\n'
                   b'Content-Type: image/png\r\n\r\n' + buffer.tobytes() + b'\r\n')

    @camfeed_blueprint.route('/video_feed')
    def video_feed():
        return Response(cameragenerator(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    return camfeed_blueprint
