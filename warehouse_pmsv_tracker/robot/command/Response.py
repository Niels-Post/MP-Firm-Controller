from enum import Enum
from typing import List

class ReturnCode(Enum):
    """
    Possible return codes for a response from the robot.
    (note that NO_RESPONSE should not be received, and is only used internally by the robot)
    """
    SUCCESS = 0
    ACTION_STARTED = 1
    ROBOT_BUSY = 2
    HARDWARE_ERROR = 3
    NO_SUCH_SENSOR = 4
    BAD_PARAMETERS = 5
    COMMAND_PARSE_ERROR = 6
    UNKOWN_COMMAND_CATEGORY = 7
    UNKNOWN_COMMAND = 8
    NO_RESPONSE = 9
    ID_ALREADY_SET = 10


class Response:
    message_id: int = 0
    return_code: ReturnCode = ReturnCode.SUCCESS
    data: List = []

    def __init__(self, data: List[int]):
        """
        Create a response object from a list of bytes
        :param data: Data to build a response from
        """
        if len(data) < 2:
            raise ValueError("Parse failed, data too short")

        self.message_id = data[0]
        self.return_code = ReturnCode(data[1])
        self.data = data[2:]

    def __repr__(self):
        return "data:" + str(self.data)
