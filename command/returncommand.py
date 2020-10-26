from typing import List

from command.returncode import ReturnCode


class ReturnCommand:
    message_id: int = 0
    return_code: ReturnCode = ReturnCode.SUCCESS
    data: List = []

    def __init__(self, data: List[int]):
        if len(data) < 2:
            raise ValueError("Parse failed, data too short")

        self.message_id = data[0]
        self.return_code = ReturnCode(data[1])
        self.data = data[2:]
