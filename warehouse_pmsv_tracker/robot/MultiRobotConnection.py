from enum import Enum
from typing import List, Dict, Tuple, Callable, NewType

import spidev
from RPi import GPIO

from warehouse_pmsv_tracker.robot.command.controllermessage import ControllerMessage
from warehouse_pmsv_tracker.robot.command.robotmessage import RobotMessage, ReturnCode
from warehouse_pmsv_tracker.robot.lib.lib_nrf24.lib_nrf24 import NRF24


class RobotAlreadyRegisteredError(RuntimeError):
    """
    Raised when a robot is registered twice to the RobotConnection handler
    """

    def __init__(self, robot_id: int):
        super("Robot with ID {} was registered twice" % robot_id)


class UnknownRobotError(RuntimeError):
    """
    Raised when RobotConnection is used to communicate with a robot that is not registered
    """

    def __init__(self, robot_id: int):
        super("Communication with unknown robot with iD {}" % robot_id)


CommandCallback = NewType("CommandCallback", Callable[[RobotMessage], None])


class CallbackStatus(Enum):
    COMMAND_SENT=0
    ACTION_STARTED=1
    FAILED=2
    SUCCESSFUL=3

class SentCommand:
    def __init__(self, callback: CommandCallback, original_message: ControllerMessage):
        self.callback = callback
        self.original_message = original_message
        self.status = CallbackStatus.COMMAND_SENT

    def update(self, message: RobotMessage):
        self.status = message.return_code
        self.callback(message)


class MultiRobotConnection:
    def __init__(self, channel: int = 50, csn_pin: int = 0, ce_pin: int = 17,
                 broadcast_write_pipe: List[int] = [0xE0, 0xE0, 0xF1, 0xF1, 0xE0],
                 broadcast_read_pipe: List[int] = [0xE0, 0xE0, 0xF1, 0xF1, 0xE0]):
        self.current_message_id = 0
        self.broadcast_write_pipe = broadcast_write_pipe
        self.broadcast_read_pipe = broadcast_read_pipe
        self._init_NRF(channel, csn_pin, ce_pin)

        self.robots: Dict[int, Tuple[List[int], List[int]]] = {}

        self.sent_commands: Dict[int, SentCommand] = dict()
        self.queues: List[List[ControllerMessage]] = []

    def _init_NRF(self, channel: int, csn_pin: int, ce_pin: int):
        GPIO.setmode(GPIO.BCM)
        self.radio = NRF24(GPIO, spidev.SpiDev())
        self.radio.begin(csn_pin, ce_pin)
        self.radio.setPayloadSize(32)
        self.radio.setChannel(channel)
        self.radio.setDataRate(NRF24.BR_1MBPS)
        self.radio.setPALevel(NRF24.PA_MAX)
        self.radio.setAutoAck(True)
        self.radio.enableDynamicPayloads()
        self.radio.openWritingPipe(self.broadcast_write_pipe)
        self.radio.openReadingPipe(0, self.broadcast_read_pipe)
        self.radio.powerUp()
        self.radio.printDetails()
        self.radio.startListening()

    def _increment_message_id(self):
        self.current_message_id = (self.current_message_id + 1) % 255

    def send_command(self, robot_id: int, cmd: ControllerMessage, callback: CommandCallback):
        if not robot_id in self.robots:
            raise UnknownRobotError(robot_id)

        self.radio.stopListening()
        self.radio.openWritingPipe(self.robots[robot_id][0])
        self.radio.write(cmd.to_bytes(self.current_message_id))
        self.radio.startListening()
        self.sent_commands[self.current_message_id] = SentCommand(callback, cmd)
        self._increment_message_id()


    def send_commandsequence(self, robot_id: int, sequence: List[ControllerMessage], immediate: bool = False):
        """
        Send a sequence of commands to a robot.

        By default each command is only sent after confirmation of the previous command.
        :param sequence: Sequence of commands to send
        :param immediate: If true, all commands are sent immediately, without waiting for confirmation
        :return:
        """
        pass

    def process_incoming_data(self):
        pipe = [0]
        if self.radio.available(pipe):
            payload = []
            length = self.radio.getDynamicPayloadSize()
            self.radio.read(payload, length)
            print("Length: " + str(length))
            print(payload)
            msg = RobotMessage(payload)
            if msg.message_id in self.sent_commands:
                self.sent_commands[msg.message_id].update(msg)









    def register_robot(self, id: int):
        if id in self.robots:
            raise RobotAlreadyRegisteredError(id)

        self.robots[id] = (
            [*self.broadcast_write_pipe[:-1], id],
            [*self.broadcast_read_pipe[:-1], id]
        )
        self.radio.openReadingPipe(len(self.robots), self.robots[id][1])
