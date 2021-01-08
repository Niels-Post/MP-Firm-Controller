from enum import Enum
from typing import List


class Category(Enum):
    GENERAL = 0
    ACTION = 1
    MEASUREMENT = 2
    CONFIGURATION = 3

class Command:
    category_id: int = 0
    command_id: int = 0
    parameters: List[int] = []

    message_id = 0

    def __init__(self, cat_id: int, cmd_id: int, params: List[int]) -> None:
        self.category_id = cat_id
        self.command_id = cmd_id
        self.parameters = params

    def to_bytes(self, message_id: int) -> List[int]:
        self.message_id = message_id
        return [
            self.category_id << 5 | (self.command_id & 0x1f),
            message_id,
            *self.parameters
        ]

    def is_response(self):
        return False

    def __repr__(self):
        string = "Cmd:" + str(self.command_id) + ","
        string += "Params:" + str(self.parameters)
        return string

