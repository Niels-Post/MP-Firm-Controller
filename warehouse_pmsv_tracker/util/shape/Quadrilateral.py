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


from typing import List

import cv2
import numpy as np

from .Coordinates import Point, calculate_points_centroid, calculate_direction_to_point, calculate_shortest_distance
from .Pose import Pose


class Quadrilateral:
    """
    Object representing an irregular quadrilateral
    """

    def __init__(self, topleft_point: Point, topright_point: Point, bottomleft_point: Point,
                 bottomright_point: Point):
        """
        Create a Quadrilateral

        Note that to preserve orientation of a shape, the topleft point in the quadrilateral does not need to be
        located in the topleft corner of the quadrilateral, instead it is the point that would be top left if
        the quadrilateral was oriented upwards
        :param topleft_point:
        :param topright_point:
        :param bottomleft_point:
        :param bottomright_point:
        """
        self.coordinates: List[Point] = [
            topleft_point,
            topright_point,
            bottomleft_point,
            bottomright_point
        ]
        self.topleft = np.asarray(topleft_point)
        self.topright = np.asarray(topright_point)
        self.bottomleft = np.asarray(bottomleft_point)
        self.bottomright = np.asarray(bottomright_point)

    def get_contour(self):
        """
        Get a OpenCV compatible contour. This can be used for shape inspection using OpenCV's functions
        :return:
        """
        return np.asarray(self.coordinates)

    def find_outer_corner(self, maximise_x: bool, maximise_y: bool) -> Point:
        """
        Find the outer corner in any combination of directions (e.g. the top left point)
        :param maximise_x: If True, find_outer_corners will look for the rightmost point, if false, the leftmost
        :param maximise_y:If True, find_outer_corners will look for the top point, if false, the bottom
        :return: The coordinates of the outer point
        """
        result = [(x if maximise_x else -x) + (y if maximise_y else -y) for x, y in self.coordinates]
        return tuple(self.coordinates[result.index(max(result))])

    def get_center(self) -> Point:
        """
        Get the center of the quadrilateral
        :return:
        """
        return calculate_points_centroid(self.coordinates)

    def get_pose(self) -> Pose:
        """
        Calculate the pose of the quadrilateral
        :return: A pose object for the quadrilateral's pose
        """
        bottom_center = calculate_points_centroid([self.bottomleft, self.bottomright])
        top_center = calculate_points_centroid([self.topleft, self.topright])
        angle = calculate_direction_to_point(bottom_center, top_center)

        return Pose(self.get_center(), angle)

    def get_minimum_horizontal_distances(self, point: Point) -> (float, float):
        """
        Calculate the shortest distances from a point to the left and right lines of the quadrilateral

        The left/right line is chosen relative to the quadrilateral, and may not be the left/right
        line as seen in the image
        :param point: Point to calculate distances for
        :return: A tuple of two distances: Distance from the point to the left line, and the distance from the point to
        the right line
        """
        return (
            calculate_shortest_distance((self.topleft, self.bottomleft), point),
            calculate_shortest_distance((self.topright, self.bottomright), point)
        )

    def get_minimum_vertical_distances(self, point: Point) -> (float, float):
        """
        Calculate the shortest distances from a point to the top and bottom lines of the quadrilateral

        The bottom/top line is chosen relative to the quadrilateral, and may not be the bottom/top line as seen in the
        image
        :param point: Point to calculate distances for
        :return: A tuple of two distances: Distance from the point to the top line, and the distance from the point to
        the bottom line
        """
        return (
            calculate_shortest_distance((self.topleft, self.topright), point),
            calculate_shortest_distance((self.bottomleft, self.bottomright), point)
        )

    def is_valid(self):
        """
        When the quadrilateral is zero-initialized, some calculations may yield DivisionByZero.
        To prevent this, is_valid can be called to assert that a quad is not zero-initialized
        :return: True if at least one of the coordinates is non-zero
        """
        return any((any(coord != 0 for coord in point) for point in self.coordinates))

    def draw(self, image, color=(255, 0, 0), writeCoordinates=False):
        """
        Draw the quadrilateral on a given image
        :param image: Image to draw the quadrilateral on
        :param color: Color in which to draw
        :param writeCoordinates: If True, draw will also write the coordinates of the quad next to the points
        :return: None
        """
        tl = tuple(int(x) for x in tuple(self.topleft))
        tr = tuple(int(x) for x in tuple(self.topright))
        bl = tuple(int(x) for x in tuple(self.bottomleft))
        br = tuple(int(x) for x in tuple(self.bottomright))

        cv2.line(image, tl, tr, color, 1)
        cv2.line(image, tl, bl, color, 1)
        cv2.line(image, tr, br, color, 1)
        cv2.line(image, bl, br, color, 1)
        cv2.circle(image, tl, 5, color)

        if writeCoordinates:
            cv2.putText(image, str(tl), tl, cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255))
            cv2.putText(image, str(tr), tr, cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255))
            cv2.putText(image, str(bl), bl, cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255))
            cv2.putText(image, str(br), br, cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255))
