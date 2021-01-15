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


from enum import IntEnum


class Category(IntEnum):
    GENERAL = 0
    ACTION = 1
    MEASUREMENT = 2
    CONFIGURATION = 3


class ActionCommand(IntEnum):
    CANCEL_MOVEMENT = 0
    START_MOVE_MM = 1
    START_ROTATE_DEGREES = 2
    SET_SPEED = 3


class ConfigurationCommand(IntEnum):
    SET_VALUE = 0
    GET_VALUE = 1
    LOAD = 2
    STORE = 3
    PRINT_ALL = 4
    GET_INFO = 5
    GET_CONFIGURATION_COUNT = 6


class GeneralCommand(IntEnum):
    REBOOT = 0
    SET_ID = 1
