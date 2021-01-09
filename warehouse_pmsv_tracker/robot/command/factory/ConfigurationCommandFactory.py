import struct

from warehouse_pmsv_tracker.robot.command import Command
from warehouse_pmsv_tracker.robot.command.registry import Category, ConfigurationCommand


class ConfigurationCommandFactory:
    category_id = Category.CONFIGURATION

    @classmethod
    def set_value(cls, config_id: int, val: str, type: str) -> Command:
        listval = []

        if type == "f":
            listval = list(struct.pack("f", float(val)))
        else:
            listval.append(int(val))



        return Command(
            cls.category_id,
            ConfigurationCommand.SET_VALUE,
            [config_id, *listval]
        )

    @classmethod
    def get_value(cls, config_id: int) -> Command:
        return Command(
            cls.category_id,
            ConfigurationCommand.GET_VALUE,
            [config_id]
        )

    @classmethod
    def get_type(cls, config_id) -> Command:
        return Command(
            cls.category_id,
            ConfigurationCommand.GET_TYPE,
            [config_id]
        )

    @classmethod
    def load(cls) -> Command:
        return Command(
            cls.category_id,
            ConfigurationCommand.LOAD,
            []
        )

    @classmethod
    def store(cls) -> Command:
        return Command(
            cls.category_id,
            ConfigurationCommand.STORE,
            []
        )

    @classmethod
    def print_all(cls) -> Command:
        return Command(
            cls.category_id,
            ConfigurationCommand.PRINT_ALL,
            []
        )