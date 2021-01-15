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


from collections import defaultdict
from typing import Dict

from flask import Blueprint, Response, jsonify

from warehouse_pmsv_tracker.robot.command.factory import ConfigurationCommandFactory, GeneralCommandFactory
from warehouse_pmsv_tracker.util import ConfigValueInformation
from warehouse_pmsv_tracker.warehouse import WarehousePMSV


def construct_configuration_blueprint(pmsv: WarehousePMSV):
    """
        Flask BluePrint to change the settings of a robot.

        :param pmsv: PMSV the robots are connected to
        :return:  The blueprint for the /config route
    """
    configuration_blueprint = Blueprint("config", __name__)

    config_count: Dict[int, int] = defaultdict(lambda: 0)
    config_values: Dict[int, Dict[int, ConfigValueInformation]] = {}
    fully_synced: Dict[int, bool] = defaultdict(lambda: False)

    @configuration_blueprint.route("/get_count/<robot_id>")
    def get_config_count(robot_id):
        """
        Requests the amount of configuration values a robot has stored
        :param robot_id: ID of the robot to query
        :return:
        """
        return jsonify(count=config_count[int(robot_id)])

    @configuration_blueprint.route("/sync_value_information/<robot_id>")
    def sync_value_information(robot_id):
        """
        Request all information about ConfigurationValues for a robot

        Warning: This route causes a lot of wireless communication with the robot and should be used sparingly
        :param robot_id: ID of the robot to query
        :return:
        """
        robot_id = int(robot_id)
        current_value = [1]

        if robot_id not in config_values:
            config_values[robot_id] = {}

        def error_callback(message_id):
            if pmsv.robots[robot_id].multi_robot_connection.clear_callback(message_id):
                pmsv.robots[robot_id].send_command(ConfigurationCommandFactory.get_info(current_value[0]), info_callback,
                                               error_callback, False)

        def count_callback(response: Response):
            config_count[robot_id] = int.from_bytes(response.data[:4], byteorder="little")
            pmsv.robots[robot_id].send_command(ConfigurationCommandFactory.get_info(current_value[0]), info_callback,
                                               None, False)

        def info_callback(resp: Response):
            tp = chr(resp.data[0])
            name = "".join([chr(ch) for ch in resp.data[1:]])
            config_values[robot_id][current_value[0]] = ConfigValueInformation(current_value[0], tp, name)
            print(config_values[robot_id][current_value[0]])
            current_value[0] += 1
            if current_value[0] <= config_count[robot_id]:
                pmsv.robots[robot_id].send_command(ConfigurationCommandFactory.get_info(current_value[0]),
                                                   info_callback, error_callback, False)
            else:
                current_value[0] = 1
                pmsv.robots[robot_id].send_command(ConfigurationCommandFactory.get_value(current_value[0]),
                                                   value_callback, value_error_callback, False)

        def value_error_callback(message_id):
            if pmsv.robots[robot_id].multi_robot_connection.clear_callback(message_id):
                pmsv.robots[robot_id].send_command(ConfigurationCommandFactory.get_info(current_value[0]), info_callback,
                                               error_callback, False)

        def value_callback(resp: Response):
            config_values[robot_id][current_value[0]].set_data(resp.data)
            current_value[0] += 1
            if current_value[0] <= config_count[robot_id]:
                pmsv.robots[robot_id].send_command(ConfigurationCommandFactory.get_value(current_value[0]),
                                                   value_callback, value_error_callback, False)
            else:
                fully_synced[robot_id] = True

        if fully_synced[robot_id]:
            fully_synced[robot_id] = False
            pmsv.robots[robot_id].send_command(ConfigurationCommandFactory.get_value(current_value[0]),
                                               value_callback, value_error_callback, False)
        else:
            pmsv.robots[robot_id].send_command(ConfigurationCommandFactory.get_configurationvalue_count(),
                                               count_callback,
                                               None, False)

        return jsonify(action="started", success=True)

    @configuration_blueprint.route("/")
    @configuration_blueprint.route("/get_all_value_information/<robot_id>")
    def get_all_value_information(robot_id):
        """
        Return all stored value information for a specific robot
        :param robot_id: ID of the robot
        :return:
        """
        robot_id = int(robot_id)
        if robot_id in config_values:
            return jsonify(result=config_values[robot_id],
                           success=fully_synced[robot_id])
        else:
            return jsonify(success=False, reason="Call request_names first.")

    @configuration_blueprint.route("/set_value/<robot_id>/<config_id>/<value>")
    def set_value(robot_id, config_id, value):
        """
        Change a specific configuration value for a robot
        :param robot_id: ID of the robot to change the value for
        :param config_id: ID of the configuration value to change
        :param value: The new value for the configurationvalue
        :return:
        """
        robot_id = int(robot_id)
        config_id = int(config_id)
        if not robot_id in config_values:
            return jsonify(success=True, reason="You need to sync value information first")

        conf_value = config_values[robot_id][config_id]
        conf_value.set(value)

        pmsv.robots[robot_id].send_command(
            ConfigurationCommandFactory.set_value(config_id, conf_value.data))

        return jsonify(success=True, data=conf_value.data)


    @configuration_blueprint.route("/store_and_reboot/<robot_id>")
    def store_and_reboot(robot_id):
        """
        Store all changed settings to the robot's ROM and reboot the robot
        :param robot_id: ID of the robot to store for
        :return:
        """
        def on_values_stored(resp: Response):
            pmsv.robots[robot_id].send_command(GeneralCommandFactory.reboot())

        pmsv.robots[int(robot_id)].send_command(
            ConfigurationCommandFactory.store(),
            on_values_stored
        )
        return jsonify(success=True)

    return configuration_blueprint


