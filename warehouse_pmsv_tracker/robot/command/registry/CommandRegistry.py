from enum import IntEnum


class Category(IntEnum):
    GENERAL = 0
    ACTION = 1
    MEASUREMENT = 2
    CONFIGURATION = 3


class ActionCommand(IntEnum):
    CANCEL_MOVEMENT = 0
    START_MOVE_MM = 1
    START_ROTATE_DEGREES = 2
    SET_SPEED = 3


class ConfigurationCommand(IntEnum):
    SET_VALUE = 0
    GET_VALUE = 1
    GET_TYPE = 2
    LOAD = 3
    STORE = 4
    PRINT_ALL = 5


class GeneralCommand(IntEnum):
    REBOOT = 0
    SET_ID = 1