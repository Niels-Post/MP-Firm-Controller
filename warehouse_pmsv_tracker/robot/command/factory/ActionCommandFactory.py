from typing import Union

from warehouse_pmsv_tracker.robot.command import Command
from warehouse_pmsv_tracker.robot.command.registry import ActionCommand, Category

from warehouse_pmsv_tracker.util import is_unsigned_compatible, is_bool_compatible


class ActionCommandFactory:
    category_id = Category.ACTION

    @classmethod
    def cancel_movement(cls) -> Command:
        return Command(
            cls.category_id,
            ActionCommand.CANCEL_MOVEMENT,
            []
        )

    @classmethod
    def start_move_mm(cls, mm: int, direction: Union[bool, None]) -> Command:
        assert is_unsigned_compatible(mm, 16)

        params = [mm >> 8, mm & 0xFF]
        if direction is not None:
            params.append(int(direction))
        return Command(
            cls.category_id,
            ActionCommand.START_MOVE_MM,
            params
        )

    @classmethod
    def start_rotate_degrees(cls, degrees: int, direction: bool):
        assert is_unsigned_compatible(degrees, 16)
        assert is_bool_compatible(direction)

        return Command(
            cls.category_id,
            ActionCommand.START_ROTATE_DEGREES,
            [degrees >> 8, degrees & 0xFF, int(direction)]
        )


    @classmethod
    def set_speed(cls, speed: int):
        assert is_unsigned_compatible(speed, 8)
        return Command(
            cls.category_id,
            ActionCommand.SET_SPEED,
            [speed]
        )






