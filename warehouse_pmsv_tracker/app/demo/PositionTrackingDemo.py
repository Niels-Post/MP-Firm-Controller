
import cv2
import numpy as np

from warehouse_pmsv_tracker.app.demo._DemoUtils_ import open_windows, is_any_closed
from warehouse_pmsv_tracker.detection.ArucoDetectionPipeline import ArucoDetectionPipeline
from warehouse_pmsv_tracker.detection.transformation.shape import Rectangle

undistortion_file = "../../../resources/cybertrack_h3_calibration.yaml"

corner_markers = [2, 4, 3, 5]

other_markers = [1, 0]

area_dimensions = Rectangle(0, 0, 1200, 650)


def PosTrackDemo():
    # Create a detection pipelin
    detection_pipeline = ArucoDetectionPipeline(undistortion_file, cv2.VideoCapture(0))

    # Have the pipeline detect and setup the area
    detection_pipeline.setup_area(corner_markers, area_dimensions)

    # Create demo windows
    windows = ["Live View", "Resulting Coordinates"]
    open_windows(windows)

    # Create an image to draw the calculated coordinates on
    coordinate_system = np.ndarray(
        [detection_pipeline.position_transformer.rect.h, detection_pipeline.position_transformer.rect.w,
         3])

    while not is_any_closed(windows):
        # Find markers 0 and 1
        image, quads, transformed_quads = detection_pipeline.find_markers(other_markers)

        # Draw all found quads on the live view
        [quad.draw(image, (0, 0, 255)) for quad in quads if quad.is_valid()]

        # Draw the pose on the live view (the pose consists of the center point and a line indicating its orientation)
        [quad.get_pose().draw(image) for quad in quads if quad.is_valid()]

        # Draw the area on the live view
        detection_pipeline.position_transformer.quad.draw(image)

        # Display the live view
        cv2.imshow("LiveView", image)

        # Clear the output view
        coordinate_system.fill(255)

        # Draw all transformed quads onto the output view
        [quad.draw(coordinate_system, (0, 0, 255)) for quad in transformed_quads if quad.is_valid()]

        # Draw all transformed poses onto the output view
        [quad.get_pose().draw(coordinate_system) for quad in transformed_quads if quad.is_valid()]

        # Draw the are on the output view
        detection_pipeline.position_transformer.rect.draw(coordinate_system)

        # Display the output view
        cv2.imshow("Coordinates", coordinate_system)

    cv2.destroyAllWindows()
    exit()


if __name__ == '__main__':
    PosTrackDemo()
