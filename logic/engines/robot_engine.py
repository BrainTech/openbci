#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import os.path, sys, time, os
from obci.gui.ugm import ugm_helper
import devices.pyrovio.rovio as rovio
from multiplexer.multiplexer_constants import peers, types
from obci.utils import context as ctx

class RobotEngine(object):
    def __init__(self, configs, context=ctx.get_dummy_context('RobotEngine')):
        self.logger = context['logger']
        self._robot = rovio.Rovio('', configs['robot_ip'])
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
            self.logger.info(result + "   command: " + command)

    def robot(self, command):
        t = time.time()
        try:
            if command == 'forward':
                self._robot_cmd(self._robot.forward, command)
            elif command == 'backward':
                self._robot_cmd(self._robot.backward, command)
            elif command == 'left':
                self._robot_cmd(self._robot.left, command)
            elif command == 'right':
                self._robot_cmd(self._robot.right, command)
            elif command == 'camera_up':
                result = self._robot.head_up()
                self.logger.info(str(result) + "command: " + command)
            elif command == 'camera_middle':
                result = self._robot.head_middle()
                self.logger.info(str(result) + "command: " + command)
            elif command == 'camera_down':
                result = self._robot.head_down()
                self.logger.info(str(result) + "command: " + command)
            else:
                self.logger.error('(rovio handling) Command ' + command + ' not supported.')
        except:
            self.logger.error("NO CONNECTION TO ROBOT!!!! COMMAND IGNORED!!! In time: "+str(time.time()-t))
            ugm_helper.send_status(self.conn, "Couldn't connect to Robot... Command ignored.")
            time.sleep(0.5)

    def start_robot_feedback(self):
        """Called eg. in mult-logic just after starting robot logic."""
        self.logger.info("Start robot feed...")
        self.conn.send_message(
            message = "start",
            type=types.ROBOT_FEEDBACK_CONTROL, 
            flush=True)

    def stop_robot_feedback(self):
        """Called eg. in mult-logic just after finishing robot logic."""
        self.logger.info("Stop robot feed...")
        self.conn.send_message(
            message = "stop",
            type=types.ROBOT_FEEDBACK_CONTROL, 
            flush=True)
        time.sleep(0.5)#make sure(?) robot feedback will not overwrite below
        ugm_helper.send_logo(self.conn, 'gui.ugm.resources.bci.png')

