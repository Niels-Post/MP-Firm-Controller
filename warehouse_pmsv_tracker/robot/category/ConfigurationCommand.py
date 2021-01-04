import struct
from typing import List

from warehouse_pmsv_tracker.robot.command.controllermessage import ControllerMessage




class ConfigurationCommand:
    category_id = 3

    @classmethod
    def set_value(cls, config_id, val: str, type: str) -> ControllerMessage:
        listval = []

        if type == "f":
            listval = list(struct.pack("f", float(val)))
        else:
            listval.append(int(val))



        return ControllerMessage(
            cls.category_id,
            0,
            [config_id, *listval]
        )

    @classmethod
    def get_value(cls, config_id) -> ControllerMessage:
        return ControllerMessage(
            cls.category_id,
            1,
            [config_id]
        )

    @classmethod
    def get_type(cls, config_id) -> ControllerMessage:
        return ControllerMessage(
            cls.category_id,
            2,
            [config_id]
        )

    @classmethod
    def load(cls) -> ControllerMessage:
        return ControllerMessage(
            cls.category_id,
            3,
            []
        )

    @classmethod
    def store(cls) -> ControllerMessage:
        return ControllerMessage(
            cls.category_id,
            4,
            []
        )

    @classmethod
    def print_all(cls) -> ControllerMessage:
        return ControllerMessage(
            cls.category_id,
            5,
            []
        )