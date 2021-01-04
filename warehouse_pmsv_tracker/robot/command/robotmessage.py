from enum import Enum
from typing import List


class ReturnCode(Enum):
    SUCCESS = 0
    ACTION_STARTED = 1
    ROBOT_BUSY = 2
    HARDWARE_ERROR = 3
    NO_SUCH_SENSOR = 4
    BAD_PARAMETERS = 5
    COMMAND_PARSE_ERROR = 6
    UNKOWN_COMMAND_CATEGORY = 7
    UNKNOWN_COMMAND = 8


class RobotMessage:
    message_id: int = 0
    return_code: ReturnCode = ReturnCode.SUCCESS
    data: List = []

    def __init__(self, data: List[int]):
        if len(data) < 2:
            raise ValueError("Parse failed, data too short")

        self.message_id = data[0]
        self.return_code = ReturnCode(data[1])
        self.data = data[2:]

    def to_string(self):
        string = "-------RobotMessage-------\n"
        string += "Message ID: \t" + str(self.message_id) + "\n"
        string += "Return Code:\t" + str(self.return_code.name) + "\n"
        string += "Data:       \t" + str(self.data) + "\n"
        string += "-----End RobotMessage-----\n"
        return string
