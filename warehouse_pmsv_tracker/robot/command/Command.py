from typing import List

from warehouse_pmsv_tracker.robot.command.registry import Category


class Command:
    """
    Class used to store a command that is sent from the controller to a robot.
    """
    category_id: int = 0
    command_id: int = 0
    parameters: List[int] = []

    message_id = 0

    def __init__(self, category_id: Category, cmd_id: int, params: List[int]) -> None:
        """
        Create a command manually (discouraged, use the factories in robot.command.factory instead)

        :param category_id: Category ID for the command (refer to robot.command.registry.CommandRegistry)
        :param cmd_id: Command ID (see above)
        :param params: List of byte parameters for the command
        """
        self.category_id: Category = category_id
        self.command_id = cmd_id
        self.parameters = params

    def to_bytes(self, message_id: int) -> List[int]:
        """
        Convert the message to bytes to be able to send it.
        :param message_id: ID of the message to insert
        :return: A list of bytes containing the message
        """
        self.message_id = message_id
        return [
            self.category_id << 5 | (self.command_id & 0x1f),
            message_id,
            *self.parameters
        ]
