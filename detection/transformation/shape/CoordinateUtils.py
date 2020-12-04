from typing import NewType, Collection, List
from typing import Tuple

import numpy as np

# Type to represent a 2-coordinate point
Point = NewType('Point', Tuple[float, float])

# Type to represent a line consisting of two points
Line = NewType('Line', Tuple[np.ndarray, np.ndarray])

# Type to represent Aruco IDs
ArucoID = NewType('ArucoID', int)

# Type to represent a square of ArucoIDs (topleft, topright, bottomleft, bottomright
ArucoSquare = NewType('ArucoSquare', Collection[ArucoID])


def calculate_shortest_distance(l: Line, p: Point) -> float:
    """
    Calculate the shortest distance from a point p to line l
    :param l: A line
    :param p: A point
    :return: The shortest distance between p and l
    """
    l1, l2 = l
    return np.linalg.norm(np.cross(l2 - l1, l1 - p)) / np.linalg.norm(l2 - l1)


def calculate_point_distance(P1: np.array, P2: np.array):
    """
    Calculate the distance between two points P1 and P2
    :param P1: Point 1
    :param P2: Point 2
    :return: The distance between P1 and P2
    """
    return np.linalg.norm(P2 - P1)


def calculate_points_centroid(points: List[Point]) -> Point:
    """
    Find the centroid of a set of points
    :param points: A list of any length of points
    :return: The coordinate of the centroid
    """
    x_coordinates: List[float] = [coord[0] for coord in points]
    y_coordinates: List[float] = [coord[1] for coord in points]
    return Point((sum(x_coordinates) / len(x_coordinates), sum(y_coordinates) / len(y_coordinates)))
