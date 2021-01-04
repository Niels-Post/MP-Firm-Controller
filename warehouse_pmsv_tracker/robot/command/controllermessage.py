from typing import List


class ControllerMessage:
    category_id: int = 0
    command_id: int = 0
    parameters: List[int] = []

    def __init__(self, cat_id: int, cmd_id: int, params: List[int]) -> None:
        self.category_id = cat_id
        self.command_id = cmd_id
        self.parameters = params

    def to_bytes(self, message_id: int) -> List[int]:
        return [
            self.category_id << 5 | (self.command_id & 0x1f),
            message_id,
            *self.parameters
        ]

    def to_string(self):
        string = "-------ControllerMessage--------\n"
        string += "Category ID:" + "\t" + str(self.category_id) + "\n"
        string += "Command ID: " + "\t" + str(self.command_id) + "\n"
        string += "Parameters: " + "\t" + str(self.parameters) + "\n"
        string += "-----End ControllerMessage------\n"
        return string

