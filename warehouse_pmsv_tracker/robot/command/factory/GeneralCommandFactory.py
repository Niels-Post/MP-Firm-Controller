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
