from enum import Enum


class ReturnCode(Enum):
    SUCCESS = 0,
    ROBOT_BUSY = 1
    HARDWARE_ERROR = 2
    MOTOR_STALL = 3
    BAD_PARAMETERS = 4
    NO_SUCH_SENSOR = 5
