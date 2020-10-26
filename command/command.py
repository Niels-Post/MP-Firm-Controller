from typing import List


class Command:
    category_id: int = 0
    command_id: int = 0
    message_id: int = 0
    parameters: List[int] = []

    def __init__(self, cat_id: int, cmd_id: int, msg_id: int, params: List[int]) -> None:
        self.category_id = cat_id
        self.command_id = cmd_id
        self.message_id = msg_id
        self.parameters = params

    def to_bytes(self) -> List[int]:
        return [self.category_id, self.command_id, self.message_id, *self.parameters]
