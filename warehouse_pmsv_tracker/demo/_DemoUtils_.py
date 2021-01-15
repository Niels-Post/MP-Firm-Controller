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


from typing import Callable, List, Any, Collection

import cv2
import numpy as np


def call_foreach(coll: Collection[Any], fun: Callable, *args):
    """
    Call a function for each item in a collection, using the given arguments

    :param coll: Collection to iterate over
    :param fun: Function to call for each item
    :param args: Arguments to pass to each function call
    :return:
    """
    for el in coll:
        fun(el, *args)


def blank_image(width: int, height: int, color: bool = True):
    """
    Generate a blank opencv image
    :param width: Width of the image
    :param height: Height of the image
    :param color: Should the image be colored
    :return: An empty image
    """
    return np.full([height, width, 3 if color else 1], 255)


def open_windows(names: List[str]):
    """
    Open several named windows and show a blank image in them
    :param names: Names of the windows to open
    :return:
    """
    blank = blank_image(10, 10)
    for name in names:
        cv2.namedWindow(name)
        cv2.imshow(name, blank)


def is_any_closed(names: List[str]):
    """
    Check if any of the given windows are closed.

    Can be used to check if the user wants to exit the application
    :param names: List of names to check for
    :return: True if any of the windows are closed
    """
    if cv2.waitKey(1) == "q":
        return True

    closed_windows = (cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE) <= 0 for name in names)

    return any(closed_windows)
