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
from typing import List


class ConfigValueInformation:
    def __init__(self, _id, _type, name):
        self.id = _id
        self.type: str = _type
        self.name: str = name
        self.data: List = []
        self.value = 0

    def _get_null_value(self):
        if self.type == "f":
            return 0.0
        elif self.type == "b":
            return True
        return 0

    def set_data(self, data: List):
        self.data = data
        self.value = self._get_raw_value_from_bytes()

    def _get_raw_value_from_bytes(self):
        if not self.data:
            return self._get_null_value()

        if self.type == "f":
            return struct.unpack("f", bytearray(self.data))[0]
        elif self.type == "i":
            return int.from_bytes(bytes(self.data), "little")
        elif self.type == "b":
            return self.data[0] > 0
        elif self.type == "c":
            return self.data[0]
        else:
            raise ValueError("Unknown Type Detected")

    def set(self, value: str):
        if self.type == "f":
            self.data = list(struct.pack("f", float(value)))
        elif self.type == "i":
            self.data = list(int(value).to_bytes(4, "little", False))
        elif self.type == "b":
            self.data = [1 if value.lower() == "true" or value == "1" else 0]
        elif self.type == "c":
            self.data = [int(value)]
        else:
            raise ValueError("Unknown Type Detected")
