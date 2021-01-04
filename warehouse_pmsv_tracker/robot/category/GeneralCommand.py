from warehouse_pmsv_tracker.robot.command.controllermessage import ControllerMessage


class GeneralCommand:
    category_id = 0
    @classmethod
    def reboot(cls):
        return ControllerMessage(
            cls.category_id,
            0,
            []
        )