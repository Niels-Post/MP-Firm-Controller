#
# Copyright (c) 2021. Niels Post. AI Lab Vrije Universiteit Brussel.
#
# This file is part of MP-Firm.
#
# MP-Firm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MP-Firm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MP-Firm.  If not, see <https://www.gnu.org/licenses/>.
#

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