#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path, sys, time, os, signal
from obci.gui.ugm import ugm_helper
import obci.devices.ar_drone.libardrone as dron
from multiplexer.multiplexer_constants import peers, types
from obci.utils import context as ctx

class RobotEngine(object):
    def __init__(self, configs, context=ctx.get_dummy_context('RobotEngine')):
         self.logger = context['logger']
         self._robot = dron.ARDrone(configs['drone_ip'], configs['drone_speed'])
         self.init_signals()
        
    def init_signals(self):
        self.logger.info("INIT SIGNALS IN APPLIANCE CLEANER")
        signal.signal(signal.SIGTERM, self.signal_handler())
        signal.signal(signal.SIGINT, self.signal_handler())
        
    def signal_handler(self):
        def handler(signum, frame):
            self.logger.info("Got signal " + str(signum) + "!!! Sending diodes ON!")
            self.robot('land')
            sys.exit(-signum)
        return handler

    def _robot_cmd(self, method, command, duration=1.0):
            result = ''
            t = time.time()
            while time.time() - t < duration:
                res = method()
            self.logger.info(result + "   command: " + command)
            if result is None:
                print "DUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUPA"

    def robot(self,command):
        t = time.time()
        self._robot.hover()
        if command == 'forward':
            self._robot_cmd(self._robot.move_forward, command, 0.7)
            
        elif command == 'backward':
            self._robot_cmd(self._robot.move_backward, command, 0.7)
            
        elif command == 'left':
            self._robot_cmd(self._robot.move_left, command, 2.5)
            
        elif command == 'right':
            self._robot_cmd(self._robot.move_right, command, 2.5)
            
        elif command == 'up':
            self._robot_cmd(self._robot.move_up, command, 4.0)
            
        elif command == 'down':
            self._robot_cmd(self._robot.move_down, command, 1.0)
            
        elif command == 'turn_right':
            self._robot_cmd(self._robot.turn_right, command, 2.7)
            
        elif command == 'turn_left':
            self._robot_cmd(self._robot.turn_left, command, 2.7)

        elif command == 'land':
            for i in range(10):
                print("******************************************* LAND "+str(i))
                self._robot.land()
                time.sleep(0.1)
            self.logger.info("land()" + "   command: " + command) 

        elif command == 'takeoff':
            for i in range(10):
                print("******************************************* TaKE OFF "+str(i))
                self._robot.takeoff()
                time.sleep(0.1)
            time.sleep(3)
            self.logger.info("takeoff()" + "   command: " + command)
            self.robot('up')
            time.sleep(1)
               
        elif command == 'reset':
            self._robot.reset()
            self.logger.info("reset()" + "   command: " + command)
