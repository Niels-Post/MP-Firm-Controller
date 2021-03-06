#
# Copyright (c) 2021. Niels Post. AI Lab Vrije Universiteit Brussel.
#
# This file is part of MP-Firm.
#
# MP-Firm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MP-Firm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MP-Firm.  If not, see <https://www.gnu.org/licenses/>.
#


import struct
from tkinter import Text, NORMAL, END, INSERT, DISABLED, Label, Entry, Button, StringVar, Tk

from warehouse_pmsv_tracker.robot import MultiRobotConnection
from warehouse_pmsv_tracker.robot.command import Command, Response
from warehouse_pmsv_tracker.robot.command.factory import ActionCommandFactory, ConfigurationCommandFactory, \
    GeneralCommandFactory

robot_id = 0x02


def set_text(text: Text, value: str):
    text.config(state=NORMAL)
    text.delete(INSERT, END)
    text.insert(INSERT, value)
    text.config(state=DISABLED)


def add_lines(text: Text, value: str):
    old_text = text.get(INSERT)
    if len(old_text) > 1:
        old_text += "\n"
    old_text += "\n" + value
    set_text(text, old_text)


class RobotConnectionDemo:
    ROW_HEIGHT = 30

    def send_and_log_command(self, message: Command, extra_callback=None):
        def cb(msg: Response):
            add_lines(self.received_commands, msg.__repr__())
            if extra_callback is not None:
                extra_callback(msg)

        add_lines(self.sent_commands, message.__repr__())
        self.connection.send_command(robot_id, message, cb)

    # START ACTION COMMANDS

    def on_move_mm(self):
        mm = int(self.input_distance_mm.get())
        direction = self.input_direction.get()
        direction = int(direction) if len(direction) > 0 else None
        self.send_and_log_command(ActionCommandFactory.start_move_mm(mm, direction))

    def add_move_mm_ui(self, offset):
        # Distance Field
        Label(self.root, text='Distance in MM', bg='#F0F8FF', font=('arial', 10, 'normal')).place(x=offset[0],
                                                                                                  y=offset[1])
        self.input_distance_mm = Entry(self.root)
        self.input_distance_mm.place(x=offset[0] + 125, y=offset[1])

        offset[1] += 30

        # Direction Field
        Label(self.root, text='Direction (0/1)', bg='#F0F8FF', font=('arial', 10, 'normal')).place(x=offset[0],
                                                                                                   y=offset[1])

        self.input_direction = Entry(self.root)
        self.input_direction.place(x=offset[0] + 125, y=offset[1])

        offset[1] += 30

        # Action Button
        Button(self.root, text='Move MM', bg='#F0F8FF', font=('arial', 10, 'normal'), command=self.on_move_mm).place(
            x=offset[0],
            y=offset[1],
            width=300)

        offset[1] += 50

    def on_rotate_degrees(self):
        degrees = int(self.input_rotation_degrees.get())
        direction = self.input_rotation_direction.get()
        direction = bool(direction)
        self.send_and_log_command(ActionCommandFactory.start_rotate_degrees(degrees, direction))

    def add_rotate_degrees_ui(self, offset):
        # Degrees rotation Input
        Label(self.root, text='Rotation in Deg', bg='#F0F8FF', font=('arial', 10, 'normal')).place(x=offset[0],
                                                                                                   y=offset[1])
        self.input_rotation_degrees = Entry(self.root)
        self.input_rotation_degrees.place(x=offset[0] + 125, y=offset[1])

        offset[1] += 30

        # Direction Input
        Label(self.root, text='Direction (0/1)', bg='#F0F8FF', font=('arial', 10, 'normal')).place(
            x=offset[0],
            y=offset[1])
        self.input_rotation_direction = Entry(self.root)
        self.input_rotation_direction.place(x=offset[0] + 125, y=offset[1])

        offset[1] += 30

        # Action Button
        Button(self.root, text='Rotate Degrees', bg='#F0F8FF', font=('arial', 10, 'normal'),
               command=self.on_rotate_degrees).place(
            x=offset[0],
            y=offset[1],
            width=300)

        offset[1] += 50

    def add_actions_ui(self, offset):
        # Actions Header
        Label(self.root, text='Actions', bg='#F0F8FF', font=('arial', 12, 'normal')).place(x=offset[0] - 15,
                                                                                           y=offset[1])
        offset[1] += 30
        self.add_move_mm_ui(offset)
        self.add_rotate_degrees_ui(offset)

    # END ACTION COMMANDS

    # START CONFIGURATION COMMANDS

    def on_set_value(self):
        def on_type_received(message: Response):
            type_char = chr(message.data[0])
            configid = int(self.config_id.get())
            val = self.value_set_value.get()
            self.send_and_log_command(ConfigurationCommandFactory.set_value(configid, val))

        configid = int(self.config_id.get())
        message = ConfigurationCommandFactory.get_type(configid)
        self.send_and_log_command(message, on_type_received)

    def add_set_value_ui(self, offset):
        # Config ID input
        Label(self.root, text='Config ID', bg='#F0F8FF', font=('arial', 10, 'normal')).place(x=offset[0], y=offset[1])
        self.config_id = Entry(self.root)
        self.config_id.place(x=offset[0] + 125, y=offset[1])

        offset[1] += 30

        # Value Input
        Label(self.root, text='Value', bg='#F0F8FF', font=('arial', 10, 'normal')).place(x=offset[0], y=offset[1])
        self.value_set_value = Entry(self.root)
        self.value_set_value.place(x=offset[0] + 125, y=offset[1])

        offset[1] += 30

        Button(self.root, text='Set Value', bg='#F0F8FF', font=('arial', 10, 'normal'),
               command=self.on_set_value).place(x=offset[0], y=offset[1], width=300)

        offset[1] += 40

    def on_get_value(self):
        # Get the type
        def on_type_received(message: Response):
            type_char = chr(message.data[0])
            self.get_type_string.set(type_char)
            configid = int(self.config_id.get())
            message = ConfigurationCommandFactory.get_value(configid)

            def on_value_received(message: Response):
                value = "ParseError"
                if type_char == "f":
                    bytestr = bytearray(message.data)
                    print(struct.unpack("f", bytestr))
                    value = struct.unpack("f", bytestr)
                elif type_char == "b":
                    value = str(bool(message.data[0]))
                elif type_char == "c":
                    value = str(message.data[0])

                self.get_value_string.set(value)

            self.send_and_log_command(message, on_value_received)

        configid = int(self.config_id.get())
        message = ConfigurationCommandFactory.get_type(configid)
        self.send_and_log_command(message, on_type_received)

    def add_get_value_ui(self, offset):
        self.get_value_string = StringVar(self.root, "Unknown")
        get_value_result = Label(self.root, text='Value', bg='#F0F8FF', font=('arial', 10, 'normal'),
                                 textvariable=self.get_value_string)
        get_value_result.place(
            x=offset[0] + 100,
            y=offset[1] + 5,
            width=200)

        Button(self.root, text='Get Value', bg='#F0F8FF', font=('arial', 10, 'normal'),
               command=self.on_get_value).place(
            x=offset[0],
            y=offset[1],
            width=100)

        offset[1] += 40

    def add_get_type_ui(self, offset):
        self.get_type_string = StringVar(self.root, "Unknown")
        get_type_result = Label(self.root, bg='#F0F8FF', font=('arial', 10, 'normal'),
                                textvariable=self.get_type_string)
        get_type_result.place(
            x=offset[0] + 100,
            y=offset[1] + 5,
            width=200)

        Label(self.root, text='Type Character', bg='#F0F8FF', font=('arial', 10, 'normal')).place(
            x=offset[0],
            y=offset[1],
            width=100)

        offset[1] += 40

    def on_print_all(self):
        self.send_and_log_command(ConfigurationCommandFactory.print_all())

    def add_print_all_ui(self, offset):
        Button(self.root, text='Print All (on Due)', bg='#F0F8FF', font=('arial', 10, 'normal'),
               command=self.on_print_all).place(
            x=offset[0],
            y=offset[1],
            width=300)
        offset[1] += 30

    def on_store(self):
        self.send_and_log_command(ConfigurationCommandFactory.store())

    def add_store_ui(self, offset):
        Button(self.root, text='Store in Flash', bg='#F0F8FF', font=('arial', 10, 'normal'),
               command=self.on_store).place(
            x=offset[0],
            y=offset[1],
            width=300)
        offset[1] += 30

    def on_load(self):
        self.send_and_log_command(ConfigurationCommandFactory.load())

    def add_load_ui(self, offset):
        Button(self.root, text='Load from Flash', bg='#F0F8FF', font=('arial', 10, 'normal'),
               command=self.on_load).place(
            x=offset[0],
            y=offset[1],
            width=300)
        offset[1] += 30

    def add_config_ui(self, offset):
        # Actions Header
        Label(self.root, text='Configuration', bg='#F0F8FF', font=('arial', 12, 'normal')).place(x=offset[0] - 15,
                                                                                                 y=offset[1])
        offset[1] += 30

        self.add_set_value_ui(offset)
        self.add_get_value_ui(offset)
        self.add_get_type_ui(offset)
        self.add_print_all_ui(offset)
        self.add_store_ui(offset)
        self.add_load_ui(offset)

    def on_reboot(self):
        self.send_and_log_command(GeneralCommandFactory.reboot())

    def add_reboot_ui(self, offset):
        Button(self.root, text='Reboot', bg='#F0F8FF', font=('arial', 10, 'normal'),
               command=self.on_reboot).place(
            x=offset[0],
            y=offset[1],
            width=300)
        offset[1] += 30

    def add_general_ui(self, offset):
        Label(self.root, text='General', bg='#F0F8FF', font=('arial', 12, 'normal')).place(x=offset[0] - 15,
                                                                                           y=offset[1])
        offset[1] += 30
        self.add_reboot_ui(offset)

    def __init__(self):
        self.connection = MultiRobotConnection()
        self.connection.register_robot(robot_id)
        self.connection.radio.printDetails()

        self.root = Tk()
        self.root.geometry('1000x800')
        self.root.configure(background='#F0F8FF')
        self.root.title('Robot Connection Demo')

        # An input field to log all messages that were sent to the robot
        self.sent_commands = Text(self.root)
        self.sent_commands.place(x=342, y=40, width=300, height=500)
        self.sent_commands.config(state=DISABLED)

        # An input field to log all messages that were received from the robot
        self.received_commands = Text(self.root)
        self.received_commands.place(x=660, y=40, width=300, height=500)
        self.received_commands.config(state=DISABLED)

        offset = [25, 25]

        self.add_actions_ui(offset)
        self.add_config_ui(offset)
        self.add_general_ui(offset)

        while True:
            self.root.update_idletasks()
            self.root.update()
            self.connection.process_incoming_data()


if __name__ == '__main__':
    demo = RobotConnectionDemo()
