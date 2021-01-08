import time
from enum import Enum
from typing import List, Dict, Tuple, Callable, NewType, Optional

import spidev
from RPi import GPIO

from warehouse_pmsv_tracker.robot.command.Command import Command
from warehouse_pmsv_tracker.robot.command.Response import Response
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


CommandCallback = NewType("CommandCallback", Callable[[Response], None])
ErrorCallback = NewType("ErrorCallback", Optional[Callable[[], None]])


class CallbackStatus(Enum):
    COMMAND_SENT = 0
    ACTION_STARTED = 1
    FAILED = 2
    SUCCESSFUL = 3


class SentCommand:
    def __init__(self, callback: CommandCallback, original_message: Command,
                 errorCallback: Optional[Callable[[], None]] = None):
        self.callback = callback
        self.time = time.time()
        self.num_responses = 0
        self.errorcallback = errorCallback
        self.original_message = original_message
        self.status = CallbackStatus.COMMAND_SENT

    def update(self, message: Response):
        self.status = message.return_code
        self.callback(message)
        self.num_responses += 1
        return False

    def is_expired(self) -> bool:
        if time.time() > (self.time + 5) and self.num_responses == 0:
            if self.errorcallback is not None:
                self.errorcallback()
            return True
        return False


class MultiRobotConnection:
    def __init__(self, channel: int = 0x10, csn_pin: int = 0, ce_pin: int = 17,
                 broadcast_write_pipe: List[int] = [0xE0, 0xE0, 0xF1, 0xF1, 0xFF],
                 broadcast_read_pipe: List[int] = [0xE0, 0xE0, 0xF1, 0xF1, 0xFF]):
        self.current_message_id = 0
        self.broadcast_write_pipe = broadcast_write_pipe
        self.broadcast_read_pipe = broadcast_read_pipe
        self._init_NRF(channel, csn_pin, ce_pin)

        self.robots: Dict[int, Tuple[List[int], List[int]]] = {0: (
            self.broadcast_write_pipe,
            self.broadcast_read_pipe
        )}

        self.sent_commands: Dict[int, SentCommand] = dict()
        self.queues: List[List[Command]] = []

    def _init_NRF(self, channel: int, csn_pin: int, ce_pin: int):
        GPIO.setmode(GPIO.BCM)
        self.radio = NRF24(GPIO, spidev.SpiDev())
        self.radio.begin(csn_pin, ce_pin)
        self.radio.setPayloadSize(32)
        self.radio.setChannel(channel)
        self.radio.setPALevel(NRF24.PA_HIGH)
        self.radio.setDataRate(NRF24.BR_250KBPS)
        self.radio.setAutoAck(True)
        self.radio.enableDynamicPayloads()
        self.radio.setRetries(5, 5)
        self.radio.openReadingPipe(0, self.broadcast_read_pipe)
        self.radio.setAutoAckPipe(0, False)
        self.radio.powerUp()
        self.radio.startListening()
        self.radio.printDetails()

    def _increment_message_id(self):
        self.current_message_id = (self.current_message_id + 1) % 255

    def broadcast_command(self, cmd: Command, callback: CommandCallback,
                          errorCallback: ErrorCallback = None):
        test = time.time()
        self.radio.stopListening()
        self.radio.openWritingPipe(self.broadcast_write_pipe)
        self.radio.write(cmd.to_bytes(self.current_message_id))
        self.radio.startListening()
        self.sent_commands[self.current_message_id] = SentCommand(callback, cmd, errorCallback)
        self._increment_message_id()
        print(test - time.time())

    def send_command(self, robot_id: int, cmd: Command, callback: CommandCallback,
                     errorCallback: Optional[Callable[[], None]] = None):
        if not robot_id in self.robots:
            raise UnknownRobotError(robot_id)

        self.radio.stopListening()
        self.radio.setAutoAckPipe(0, True)
        self.radio.openWritingPipe(self.robots[robot_id][0])
        success = self.radio.write(cmd.to_bytes(self.current_message_id))
        self.radio.setAutoAckPipe(0, False)

        self.radio.startListening()
        if not success and errorCallback is not None:
            errorCallback()
        self.sent_commands[self.current_message_id] = SentCommand(callback, cmd, errorCallback)
        self._increment_message_id()

        print("Sent ({}): {}".format(robot_id, cmd))
        if not success:
            print("<<<<<<<<<<<<FAILED>>>>>>>>>>>>>")
        self.radio.print_observe_tx()

    def send_commandsequence(self, robot_id: int, sequence: List[Command], immediate: bool = False):
        """
        Send a sequence of commands to a robot.

        By default each command is only sent after confirmation of the previous command.
        :param sequence: Sequence of commands to send
        :param immediate: If true, all commands are sent immediately, without waiting for confirmation
        :return:
        """
        raise NotImplementedError()

    def process_incoming_data(self):
        pipe = [0]
        if self.radio.available(pipe):
            payload = []
            length = self.radio.getDynamicPayloadSize()
            self.radio.read(payload, length)
            msg = Response(payload)

            print("Recv ({}): {}".format(pipe[0], msg))

            if msg.message_id in self.sent_commands:
                if self.sent_commands[msg.message_id].update(msg):
                    del self.sent_commands[msg.message_id]
        keys = []

        for sent_command_id in self.sent_commands.keys():
            if self.sent_commands[sent_command_id].is_expired():
                keys.append(sent_command_id)

        for key in keys:
            self.sent_commands.pop(key, "None")

    def register_robot(self, id: int):
        if id in self.robots:
            raise RobotAlreadyRegisteredError(id)

        self.robots[id] = (
            [*self.broadcast_write_pipe[:-1], id],
            [*self.broadcast_read_pipe[:-1], id]
        )
        print(self.robots)
        self.radio.openReadingPipe(len(self.robots) - 1, self.robots[id][1])

    def is_registered(self, id: int):
        return id in self.robots
