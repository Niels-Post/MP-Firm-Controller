"""
    To keep the costs of this project as low as possible, a regular webcam can be used to track the robot.
    However, most consumer webcams don't take perfect media. Images are slightly distorted.
    This can mean that (for example) a line that is straight in real life, shows as curved on the webcam's image.

    To correct for this, media are undistorted before being used in the tracker. To do this, a camera undistortion
    matrix and distortion coefficients are needed. Both of these are specific to the model of camera, so make sure the
    model camera matches the undistortion file being used (default is a cybertrack H3 webcam). To generate new calibration
    files, refer to hhtp://link-here.


    The demo shows a live view of the webcam, and draws an overlay of the detected markers over it.

    Requirements
    ----------------

    - A USB Webcam
    - An undistortion file matching the webcam
    - (Recommended) A sheet of paper with straight lines drawn/printed on it to easily see the difference between media

    Test Setup
    ----------------

    To run the aruco demo, connect a webcam to computer and start the demo. Three windows should show:
    - The original image. When holding the sheet of paper in front of it, the straight lines will likely appear curved
    - An undistorted image, the lines should be straighter in this image, but parts of the image will be black
    - An undistorted image, cropped to the Region Of Interest. Lines should appear straighter, and no parts of the image
    are black


    Execution
    ----------------
    To execute the demo, run the following code in the root of the project:

    .. code-block:: console

        $ python3 -m pip install -r requirements.txt
        $ cd app/demo
        $ python3 CameraUndistortionDemo.py


    Example
    ---------------------
    .. image:: /_static/CameraUndistortionDemo_ScreenShot.png
           :width: 600


    Source Code
    ---------------

"""




import cv2

from warehouse_pmsv_tracker.demo._DemoUtils_ import open_windows, is_any_closed
from warehouse_pmsv_tracker.detection.calibration.CameraUndistortion import CameraUndistortion

def camera_undistortion_demo():
    """
    Runs the Camera Undistortion Demo
    :return:
    """
    print("Showing Previews of camera undistortion")
    print("Press q to exit...")

    windows = ["Original", "Undistorted", "Undistorted_Cropped"]

    # Open all windows
    open_windows(windows)

    # Create an OpenCV camera capture
    capture_device = cv2.VideoCapture(0)

    # Create a camera undistorter for the webcam used for the PMSV
    undistortion = CameraUndistortion("../../resources/cybertrack_h3_calibration.yaml")

    while not is_any_closed(windows):
        # Retrieve an image from the webcam
        success, original = capture_device.read()

        if not success:
            continue

        # Create an undistorted image without cropping
        # Without cropping, the resulting image will not be a full rectangle, but contain black parts
        undistorted = undistortion.undistort(original, False)

        # Create an undistorted image and crop it to the region of interest
        # No black parts should appear in this image, but the resulting image will be smaller
        undistorted_cropped = undistortion.undistort(original, True)

        # Show the input image and both undistorted media in seperate windows
        cv2.imshow(windows[0], original)
        cv2.imshow(windows[1], undistorted)
        cv2.imshow(windows[2], undistorted_cropped)
    cv2.destroyAllWindows()
    exit(0)


if __name__ == '__main__':
    camera_undistortion_demo()
