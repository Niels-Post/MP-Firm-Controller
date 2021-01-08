from typing import Union

from warehouse_pmsv_tracker.robot.command.Command import Command
from warehouse_pmsv_tracker.util.Assertion import is_unsigned_compatible, is_bool_compatible


class ActionCommand:
    category_id = 1

    @classmethod
    def cancel_movement(cls) -> Command:
        return Command(
            cls.category_id,
            0,
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
            1,
            params
        )

    @classmethod
    def start_rotate_degrees(cls, degrees: int, direction: bool):
        assert is_unsigned_compatible(degrees, 16)
        assert is_bool_compatible(direction)

        return Command(
            cls.category_id,
            2,
            [degrees >> 8, degrees & 0xFF, int(direction)]
        )


    @classmethod
    def set_speed(cls, speed: int):
        assert is_unsigned_compatible(speed, 8)
        return Command(
            cls.category_id,
            3,
            [speed]
        )






