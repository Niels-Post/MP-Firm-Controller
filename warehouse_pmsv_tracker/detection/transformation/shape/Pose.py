import cv2
import numpy as np
from flask import json

from warehouse_pmsv_tracker.detection.transformation.shape import Point


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
