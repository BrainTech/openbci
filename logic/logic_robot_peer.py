#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import os.path, sys, time, os
#import speller_graphics_manager as sgm

from multiplexer.multiplexer_constants import peers, types

from configs import settings, variables_pb2
from logic import logic_logging as logger
from gui.ugm import ugm_helper

from logic import logic_speller_peer
import devices.pyrovio.rovio as rovio

LOGGER = logger.get_logger("logic_robot", "info")

class LogicRobot(logic_speller_peer.LogicSpeller):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        super(LogicRobot, self).__init__(addresses=addresses)
        self._robot = rovio.Rovio('', self.get_param('robot_ip'))
        self._rc = rovio.RovioController(self._robot)
        self._rc.start()

    # --------------------------------------------------------------------------
    # ------------------ actions available in config ---------------------------

    def _robot_cmd(self, method, command):
            result = ''
            for i in range(7):
                res = method()
                result += str(res) + '.'
            # result = self._rc.enqueue_all([[900, self._robot.forward]])
            LOGGER.info(result + "   command: " + command)

    def robot(self, command):
        if command == 'forward':
            self._robot_cmd(self._robot.forward, command)

            # result = self._rc.enqueue_all([[900, self._robot.forward]])

        elif command == 'backward':
            self._robot_cmd(self._robot.backward, command)
            # result = self._rc.enqueue_all([[900, self._robot.backward]])

        elif command == 'left':
            # result = self._rc.enqueue_all([[900, self._robot.left]])
            self._robot_cmd(self._robot.left, command)
        elif command == 'right':
            self._robot_cmd(self._robot.right, command)

        elif command == 'camera_up':

            result = self._robot.head_up()

            LOGGER.info(str(result) + "command: " + command)
        elif command == 'camera_middle':
            result = self._robot.head_middle()

            LOGGER.info(str(result) + "command: " + command)
        elif command == 'camera_down':
            result = self._robot.head_down()

            LOGGER.info(str(result) + "command: " + command)
        else:
            LOGGER.error('(rovio handling) Command ' + command + ' not supported.')

    def set_field_color(self, color_name):
        pass

if __name__ == "__main__":
    LogicRobot(settings.MULTIPLEXER_ADDRESSES).loop()

