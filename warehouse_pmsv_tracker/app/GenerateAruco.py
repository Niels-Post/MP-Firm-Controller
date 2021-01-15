"""
This file generates 2 sets of printable aruco codes: big and small.

The small codes are meant to be pasted on robots to be able to identify and track them.

The big codes are meant to mark the testing area the robots will work in
"""

from warehouse_pmsv_tracker.detection.aruco import Aruco
import os

if __name__ == '__main__':
    Aruco.generate_marker_pairs(20, "../../resources/aruco_markers/big", )
    Aruco.generate_marker_pairs(20, "../../resources/aruco_markers/small", big=False)