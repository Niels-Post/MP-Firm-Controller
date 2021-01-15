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


from warehouse_pmsv_tracker.robot.command import Command
from warehouse_pmsv_tracker.robot.command.registry import Category, GeneralCommand


class GeneralCommandFactory:
    category_id = Category.GENERAL

    @classmethod
    def reboot(cls):
        return Command(
            cls.category_id,
            GeneralCommand.REBOOT,
            []
        )

    @classmethod
    def set_id(cls, id: int):
        return Command(
            cls.category_id,
            GeneralCommand.SET_ID,
            [id]
        )
