"""
    When positioning a ceilingmounted camera, it can be assumed that the camera view is not exactly perpendicular
    to the ground.

    Because of this, a rectangular area in the real world, will likely not be a rectangle in image space,
    but an irregular quadrilateral. To be able to extract real-world coordinates from the image, positions in this
    quadrilateral need to be mapped to the coordinates of the real world.
"""

import cv2
import numpy as np

from warehouse_pmsv_tracker.detection.transformation import PositionTransformer
from warehouse_pmsv_tracker.detection.transformation.shape import Quadrilateral, Rectangle, Point

mouse_is_down = False


def mouse_callback(event, x, y, flags, params):
    global mouse_is_down

    quad, rect, transformer, width, height = params


    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_is_down = True
    elif event == cv2.EVENT_LBUTTONUP:
        mouse_is_down = False

    if event == cv2.EVENT_MOUSEMOVE and mouse_is_down:
        # Create two blank media
        quad_image = np.full([height, width, 3], 255)
        rect_image = np.full([height, width, 3], 255)

        # Draw both shapes to their window
        quad.draw(quad_image)
        rect.draw(rect_image)

        # Draw a cursor indicator on the input image
        cv2.circle(quad_image, (int(x), int(y)), 5, (0, 0, 255))

        # Calculate the transformed position and draw it on the output image
        if cv2.pointPolygonTest(quad.get_contour(), (x, y), False) > 0:
            newX, newY = transformer.get_transformed_position((x, y))
            cv2.circle(rect_image, (int(newX), int(newY)), 5, (0, 0, 255))

        # Show both windows
        cv2.imshow("Output", rect_image)
        cv2.imshow("Input", quad_image)



def PositionTransformerDemo():
    width = 150
    height = 150

    # Create a quadrilateral to map from
    quad = Quadrilateral(
        Point(10, 10),
        Point(110, 11),
        Point(10, 150),
        Point(100, 100)
    )

    # Create the "real world" area rectangle.
    # Sizes can represent any chosen unit
    rect = Rectangle(10, 10, 90, 90)

    # Create a positiontransformer using the quadrilateral and the rectangle
    transformer = PositionTransformer(quad, rect)

    cv2.namedWindow("Input")
    cv2.namedWindow("Output")

    # Functionality for this demo will be executed in the mouse handler
    cv2.setMouseCallback("Input", mouse_callback, (quad, rect, transformer, width, height))

    while cv2.waitKey(1) != ord("q"):
        pass


if __name__ == '__main__':
    PositionTransformerDemo()
