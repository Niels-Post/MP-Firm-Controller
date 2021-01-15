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


import numpy as np
import cv2

from .Coordinates import Point

class Pose:
    """
        Object to store information about a Pose (Position + Angle)
    """

    def __init__(self, position: Point, angle: float):
        self.position = position
        self.angle = angle

    """
    Draw the pose to an image
    
    A pose is represented as a circle indicating the position, and a line indicating the direction.
    """

    def draw(self, image: np.ndarray, position_color=(255, 0, 0), angle_color=(0, 255, 0)):
        try:
            start_position = (int(self.position[0]), int(self.position[1]))

            radians = self.angle / 180 * np.pi
            delta_x = (15 * np.cos(radians))
            delta_y = (15 * np.sin(radians))

            end_position = int(self.position[0] + delta_x), int(self.position[1] + delta_y)
            cv2.circle(image, start_position, 2, position_color)
            cv2.line(image, start_position, end_position, angle_color)
        except ValueError:
            pass

    def __sub__(self, other):
        pos = (self.position[0] - other.position[0], self.position[1] - other.position[1])
        return Pose(pos, self.angle - other.angle)

    def __repr__(self):
        return "Pose(" + str(self.position) + "," + str(self.angle) + ")"
