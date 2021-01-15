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

from .Coordinates import Point


class Rectangle:
    """
    An object representing a rectangle
    """

    def __init__(self, x: float, y: float, w: float, h: float):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def get_xy_from_uv(self, u: float, v: float) -> Point:
        """
        Calculate x,y coordinates within the rectangle from given u,v coordinates
        :param u: U coordinate between 0 and 1
        :param v: V coordinate between 0 and 1
        :return: A point of the resulting x,y coordinates
        """
        x = self.x + (self.w * u)
        y = self.y + (self.h * v)
        return x, y

    def draw(self, image: np.ndarray, color=(255, 0, 0)):
        """
        Draw the rectangle on an image
        :param image: Image to draw on
        :param color: Color to draw the rectangle in
        :return:
        """
        cv2.rectangle(image, (self.x, self.y), (self.x + self.w, self.y + self.h), color, 1)
