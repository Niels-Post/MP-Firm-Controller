Position Tracking Demo
##########################

To make it easy to find the position of the robot, all computer vision detection steps are combined into
a single Position Detection Pipeline. This demo showcases the abilities of that pipeline.


The demo shows two windows:
- A live view of the webcam, with the square and detected markers outlined
- A corrected topdown view of the coordinate space and the position of the markers in it

Requirements
----------------

- A USB Webcam, mounted to a high point aimed at the floor
- An undistortion file matching the webcam
- (Minimum) 5 aruco markers (with differing and known id's)

Test Setup
----------------

Lay the markers on the floor so that 4 of the markers form a square. Measure the dimensions of the square.
Put the remaining marker(s) in the square.
Make sure all markers are in view of the webcam.

Setup the configuration parameters of the demo:
*undistortion_file* The undistortion file for the connected webcam
*corner_markers* The id's of the markers used for the square (in order: [topleft, topright, bottomleft, bottomright])
*other_markers* The ids of the remaining markers
*area_dimensions* A Rectangle object containing the dimensions of the square (x and y can be left at 0). The
dimension only impacts through its aspect ratio, and can therefore be expressed in any measurement unit.

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
.. video:: ../_static/PositionTrackingDemo.mp4
   :width: 500
   :height: 300


Source Code
------------

.. autofunction:: app.demo.CameraUndistortionDemo.camera_undistortion_demo
