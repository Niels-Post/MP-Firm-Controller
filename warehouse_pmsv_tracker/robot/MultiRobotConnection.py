import time
from enum import IntEnum
from typing import Callable, Optional, NewType, List, Dict, Tuple

from RPi import GPIO
from spidev import SpiDev

from warehouse_pmsv_tracker.robot.command import Response, Command
from warehouse_pmsv_tracker.robot.lib import NRF24


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
ErrorCallback = NewType("ErrorCallback", Optional[Callable[[int], None]])


class CallbackStatus(IntEnum):
    COMMAND_SENT = 0
    ACTION_STARTED = 1
    FAILED = 2
    SUCCESSFUL = 3


class _SentCommand:
    def __init__(self, callback: CommandCallback, original_message: Command,
                 errorCallback: Optional[Callable[[int], None]] = None):
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
        if time.time() > (self.time + 2) and self.num_responses == 0:
            if self.errorcallback is not None:
                self.errorcallback(self.original_message.message_id)
            return True
        return False


class MultiRobotConnection:
    def __init__(self, channel: int = 0x10, csn_pin: int = 0, ce_pin: int = 17,
                 broadcast_write_pipe: List[int] = [0xE0, 0xE0, 0xF1, 0xF1, 0xFF],
                 broadcast_read_pipe: List[int] = [0xE0, 0xE0, 0xF1, 0xF1, 0xFF]):
        """
        Initialize a multi robot connection
        :param channel: NRF channel to use for connecting (must match the robots' setting)
        :param csn_pin: CSN Pin the NRF is connected to
        :param ce_pin:  CE pin the NRF is connected to
        :param broadcast_write_pipe: Pipe to write broadcast messages to (make sure the last byte is always FF)
        :param broadcast_read_pipe:  Pipe to read broadcast responses from (make sure the last byte is always FF)
        """
        self.current_message_id = 0
        self.broadcast_write_pipe = broadcast_write_pipe
        self.broadcast_read_pipe = broadcast_read_pipe
        self._init_NRF(channel, csn_pin, ce_pin)

        self.robots: Dict[int, Tuple[List[int], List[int]]] = {0: (
            self.broadcast_write_pipe,
            self.broadcast_read_pipe
        )}

        self.sent_commands: Dict[int, _SentCommand] = dict()
        self.queues: List[List[Command]] = []

    def _init_NRF(self, channel: int, csn_pin: int, ce_pin: int):
        GPIO.setmode(GPIO.BCM)
        self.radio = NRF24(GPIO, SpiDev())
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
        """
        Send a broadcast command. This will reach all robots.

        Avoid using this method for action and measurement commands
        :param cmd: Command to broadcast
        :param callback: Function to be called when a response is received
        :param errorCallback: Function to be called when no robot responds within the allowed time
        :return:
        """
        self.radio.stopListening()
        self.radio.openWritingPipe(self.broadcast_write_pipe)
        self.radio.write(cmd.to_bytes(self.current_message_id))
        self.radio.startListening()
        self.sent_commands[self.current_message_id] = _SentCommand(callback, cmd, errorCallback)
        self._increment_message_id()

    def clear_callback(self, message_id) -> bool:
        if message_id in self.sent_commands:
            del self.sent_commands[message_id]
            return True
        return False

    def send_command(self, robot_id: int, cmd: Command, callback: CommandCallback,
                     errorCallback: Optional[Callable[[int], None]] = None):
        """
        Send a command to a single robot.

        Make sure the robot is registered using register_robot before sending commands to it
        :param robot_id: ID of the robot to send to
        :param cmd: Command to send to
        :param callback: Function to be called when the robot sends a response
        :param errorCallback: Function to be called when the robot cannot be reached, or the robot does not respond
        :return:
        """
        if not robot_id in self.robots:
            raise UnknownRobotError(robot_id)

        self.radio.stopListening()
        self.radio.setAutoAckPipe(0, True)
        self.radio.openWritingPipe(self.robots[robot_id][0])
        success = self.radio.write(cmd.to_bytes(self.current_message_id))
        self.radio.setAutoAckPipe(0, False)

        self.radio.startListening()
        if not success and errorCallback is not None:
            errorCallback(self.current_message_id)
        self.sent_commands[self.current_message_id] = _SentCommand(callback, cmd, errorCallback)
        self._increment_message_id()

    def process_incoming_data(self):
        """
        Poll the NRF for incoming data, and parse responses received.

        When a response is received, when applicable, its callbacks are called.

        This method also checks if any commands waiting for response are expired
        :return:
        """

        pipe = [0]
        if self.radio.available(pipe):
            payload = []
            length = self.radio.getDynamicPayloadSize()
            self.radio.read(payload, length)
            msg = Response(payload)

            if msg.message_id in self.sent_commands:
                if self.sent_commands[msg.message_id].update(msg):
                    del self.sent_commands[msg.message_id]
        keys = []

        for sent_command_id in list(self.sent_commands.keys()):
            if sent_command_id in self.sent_commands:
                if self.sent_commands[sent_command_id].is_expired():
                    keys.append(sent_command_id)

        for key in keys:
            self.sent_commands.pop(key, "None")

    def register_robot(self, id: int):
        """
        Register a robot for sending commands to. Note that this does not do any communication with the robot.
        :param id: ID of the robot to register
        :return:
        """
        if id in self.robots:
            raise RobotAlreadyRegisteredError(id)

        self.robots[id] = (
            [*self.broadcast_write_pipe[:-1], id],
            [*self.broadcast_read_pipe[:-1], id]
        )
        self.radio.openReadingPipe(len(self.robots) - 1, self.robots[id][1])

    def is_registered(self, id: int):
        """
        Check if a robot is registered
        :param id:
        :return:
        """
        return id in self.robots

    def unregister_robot(self, id):
        """
        Unregister a robot
        :param id: ID of the robot to unregister
        :return:
        """
        del self.robots[id]
