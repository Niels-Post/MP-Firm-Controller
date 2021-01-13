from warehouse_pmsv_tracker.detection.aruco import Aruco
import os

if __name__ == '__main__':
    Aruco.generate_marker_pairs(20, "../../resources/aruco_markers/big", )
    Aruco.generate_marker_pairs(20, "../../resources/aruco_markers/small", big=False)