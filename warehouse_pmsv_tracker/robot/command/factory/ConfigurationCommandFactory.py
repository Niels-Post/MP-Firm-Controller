import struct
from typing import List

from warehouse_pmsv_tracker.robot.command import Command
from warehouse_pmsv_tracker.robot.command.registry import Category, ConfigurationCommand


class ConfigurationCommandFactory:
    category_id = Category.CONFIGURATION

    @classmethod
    def set_value(cls, config_id: int, val: List[int]) -> Command:
        return Command(
            cls.category_id,
            ConfigurationCommand.SET_VALUE,
            [config_id, *val]
        )

    @classmethod
    def get_value(cls, config_id: int) -> Command:
        return Command(
            cls.category_id,
            ConfigurationCommand.GET_VALUE,
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

    @classmethod
    def get_info(cls, configuration_id: int):
        return Command(
            cls.category_id,
            ConfigurationCommand.GET_INFO,
            [configuration_id]
        )

    @classmethod
    def get_configurationvalue_count(cls):
        return Command(
            cls.category_id,
            ConfigurationCommand.GET_CONFIGURATION_COUNT,
            []
        )