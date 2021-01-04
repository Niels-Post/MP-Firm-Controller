import cv2

from warehouse_pmsv_tracker.app.demo._DemoUtils_ import open_windows, is_any_closed
from warehouse_pmsv_tracker.detection.aruco import Aruco


def aruco_demo():
    """
    Runs the Aruco Demo
    :return:
    """
    print("Showing Live image with Marker overlay")
    print("Press q to exit...")

    # Create the Aruco Detector
    ar = Aruco()

    # Create an OpenCV camera capture
    capture = cv2.VideoCapture(0)

    # The title of the demo window
    demo_window = "Aruco Demo"

    # Create a window to display the live view in
    open_windows([demo_window])

    while not is_any_closed([demo_window]):
        # Get an image from the webcam
        success, image = capture.read()

        # Flip the image horizontally (since webcam hardware often does this, and we don't need that for this)
        # Normally this flip is done by CameraUndistortion
        image = cv2.flip(image, 0)

        if not success:
            continue

        # Process a new image from the webcam
        detection_results = ar.process(image)

        # Draw all markers onto the image
        detection_results.draw(image)

        # Display image with overlay
        cv2.imshow(demo_window, image)

    cv2.destroyAllWindows()
    exit(0)


if __name__ == '__main__':
    aruco_demo()
