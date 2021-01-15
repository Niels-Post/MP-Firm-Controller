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


import cv2
from flask import Blueprint, Response

from warehouse_pmsv_tracker.warehouse import WarehousePMSV


def construct_camfeed_blueprint(pmsv: WarehousePMSV):
    """
    Flask Blueprint to add a live webstream

    IMPORTANT: Because of the way flask handles multitasking, this endpoint also updates the PMSV each frame (processing
    incoming wireless data and processing computer vision).
    Because of this, the PMSV is not updated when this stream is not running.

    :param pmsv: PMSV that is updated each frame
    :return:  The blueprint for the webcam route
    """
    camfeed_blueprint = Blueprint("camfeed", __name__)

    def cameragenerator():
        """
        Flask Generator. Continuously yields a webcamframe, while updating the PMSV
        :return: Seperate frames
        """
        while True:
            pmsv.update()
            retval, buffer = cv2.imencode('.png', pmsv.detection_pipeline.undistorted_image)
            yield (b'--frame\r\n'
                   b'Content-Type: image/png\r\n\r\n' + buffer.tobytes() + b'\r\n')

    @camfeed_blueprint.route('/video_feed')
    def video_feed():
        """
        Return a response that uses the cameragenerator to produce frames
        :return:
        """
        return Response(cameragenerator(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    return camfeed_blueprint
