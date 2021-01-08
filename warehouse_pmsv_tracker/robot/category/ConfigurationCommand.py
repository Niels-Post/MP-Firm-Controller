import struct
from typing import List

from warehouse_pmsv_tracker.robot.command.Command import Command




class ConfigurationCommand:
    category_id = 3

    @classmethod
    def set_value(cls, config_id, val: str, type: str) -> Command:
        listval = []

        if type == "f":
            listval = list(struct.pack("f", float(val)))
        else:
            listval.append(int(val))



        return Command(
            cls.category_id,
            0,
            [config_id, *listval]
        )

    @classmethod
    def get_value(cls, config_id) -> Command:
        return Command(
            cls.category_id,
            1,
            [config_id]
        )

    @classmethod
    def get_type(cls, config_id) -> Command:
        return Command(
            cls.category_id,
            2,
            [config_id]
        )

    @classmethod
    def load(cls) -> Command:
        return Command(
            cls.category_id,
            3,
            []
        )

    @classmethod
    def store(cls) -> Command:
        return Command(
            cls.category_id,
            4,
            []
        )

    @classmethod
    def print_all(cls) -> Command:
        return Command(
            cls.category_id,
            5,
            []
        )