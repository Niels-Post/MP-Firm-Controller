from typing import Callable

import cv2
import numpy as np


def call_foreach(coll, fun: Callable, *args):
    for el in coll:
        fun(el, *args)


def blank_image(width: int, height: int, color: bool = True):
    return np.ndarray([height, width, 3 if color else 1])


def open_windows(names: list):
    blank = blank_image(10, 10)
    for name in names:
        cv2.namedWindow(name)
        cv2.imshow(name, blank)


def is_any_closed(names: list):
    if cv2.waitKey(1) == "q":
        return True

    closed_windows = (cv2.getWindowProperty(name, cv2.WND_PROP_VISIBLE) <= 0 for name in names)

    return any(closed_windows)



if __name__ == '__main__':
    windows = ["test", "test2", "test3"]
    open_windows(windows)
    while not is_any_closed(windows):
        print("test")
    cv2.destroyAllWindows()
    exit()