from warehouse_pmsv_tracker.robot.command.Command import Command


class GeneralCommand:
    category_id = 0
    @classmethod
    def reboot(cls):
        return Command(
            cls.category_id,
            0,
            []
        )

    @classmethod
    def set_id(cls, id: int):
        return Command(
            cls.category_id,
            1,
            [id]
        )