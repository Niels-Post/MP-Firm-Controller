Aruco Demo
############

This demo aims to show the Aruco detection feature in a simple way.

The demo shows a live view of the webcam, and draws an overlay of the detected markers over it.

Requirements
----------------

- A USB Webcam
- Printed aruco codes

Test Setup
----------------

To run the aruco demo, connect a webcam to computer and start the demo. A window should appear displaying a live
webcam feed. When you hold one of the aruco codes in front of the camera, the live window should outline the code,
and display the ID of the code.


Execution
----------------
To execute the demo, run the following code in the root of the project:

.. code-block:: console

    $ python3 -m pip install -r requirements.txt
    $ cd app/demo
    $ python3 ArucoDemo.py


Example
---------------------
.. image:: /_static/ArucoDemo_ScreenShot.png
       :width: 600


Source Code
-------------

.. autofunction:: app.demo.ArucoDemo.aruco_demo
