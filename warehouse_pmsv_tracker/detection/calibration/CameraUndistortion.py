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

import numpy as np

class CameraUndistortion:
    """
    A class to help with removing the distortion from media created by the webcam's imperfection

    CameraUndistortion tries to remove both radial and tangential distortion.
    It can also flip the camera image, since webcam hardware often flips the image once in advance.
    """

    def __init__(self, calibration_file: str, flip_image: bool = True):
        """
        Create a CameraUndistortion

        :param calibration_file: Relative (from the working directory) path to a calibration file for the connected camera
        :param flip_image: Should the image be flipped?
        """
        fs = cv2.FileStorage(calibration_file, cv2.FILE_STORAGE_READ)
        self.flip_image = flip_image
        self._camera_matrix = fs.getNode("camera_matrix").mat()
        self._distortion_coefficients = fs.getNode("distortion_coefficients").mat()
        self._new_camera_matrix = None
        self._region_of_interest = (0, 0, 0, 0)
        self._map_x = self._map_y = None

    def _init(self, image):
        h, w = image.shape[:2]
        self._new_camera_matrix, self._region_of_interest = cv2.getOptimalNewCameraMatrix(self._camera_matrix,
                                                                                          self._distortion_coefficients,
                                                                                          (w, h), 1,
                                                                                          (w, h))

        self._map_x, self._map_y = cv2.initUndistortRectifyMap(self._camera_matrix, self._distortion_coefficients, None,
                                                               self._new_camera_matrix, (w, h), cv2.CV_32FC1)

    def undistort(self, image, crop_region_of_interest: bool = True) -> np.ndarray:
        """
        Get an undistorted (and possibly flipped) copy of a given image
        :param image: The image to undistort
        :param crop_region_of_interest: When true, the output image is cropped to its region of interest
        :return:
        """
        if self._new_camera_matrix is None:
            self._init(image)

        output = image.copy()
        if self.flip_image:
            output = cv2.flip(output, 0)
        output = cv2.remap(output, self._map_x, self._map_y, cv2.INTER_LINEAR)

        if crop_region_of_interest:
            x, y, w, h = self._region_of_interest
            output = output[y:y + h, x:x + w]

        return output
