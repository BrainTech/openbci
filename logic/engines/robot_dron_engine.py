import os.path, sys, time, os
from obci.gui.ugm import ugm_helper
import obci.devices.python-ardron.libardrone as dron
from multiplexer.multiplexer_constants import peers, types
from obci.utils import context as ctx

class RobotEngine(object):
    def __init__(self, context=ctx.get_dummy_context('RobotEngine')):
         self.logger = context['logger']
         self._robot = dron.ARDrone()
         self.init_signals()
         self.robot_takeoff()

 #def robot_must_done(self, command):
 #    t = time.time()
 #    running = False
 #    while not running:
 #        try:
 #            if command == 'takeoff':
 #                self._robot.takeoff() 
 #                self.logger.info("takeoff()" + "   command: " +  command)
 #                running = True
 #            elif command == 'hover':
 #                self._robot.hover()
 #                self.logger.info("hover()" + "   command: " +  command)
 #        except:
 #            self.logger.error("NO CONNECTION TO ROBOT!!!! It tries again!!! In time: " + str(time.time()-t))
 #            ugm_helper.send_status(self.conn, "Couldn't connect to Robot... It tries again.")
 #            time.sleep(0.5)


    def init_signals(self):
        self.logger.info("INIT SIGNALS IN APPLIANCE CLEANER")
        signal.signal(signal.SIGTERM, self.signal_handler())
        signal.signal(signal.SIGINT, self.signal_handler())
        
    def signal_handler(self):
        def handler(signum, frame):
            self.logger.info("Got signal " + str(signum) + "!!! Sending diodes ON!")
            self.robot.land()
            sys.exit(-signum)
        return handler

    def robot(self,command):
        t = time.time()
        try: 
            if command == 'forward':
                self._robot.move_forward()
                self.logger.info("move_forward()" + "   command: " + command)
                self._robot.hover()
            elif command == 'backward':
                self._robot.move_backward()
                self.logger.info("move_backward()" + "   command: " + command)
                self._robot.hover()
            elif command == 'left':
                self._robot.move_left()
                self.logger.info("move_left()" + "   command: " + command)
                self._robot.hover()
            elif command == 'right':
                self._robot.move_right()
                self.logger.info("move_right()" + "   command: " + command)
                self._robot.hover()
            elif command == 'up':
                self._robot.move_up()
                self.logger.info("move_up()" + "   command: " + command)
                self._robot.hover()
            elif command == 'down':
                self._robot.move_down()
                self.logger.info("move_up()" + "   command: " + command)
                self._robot.hover()
             elif command == 'turn_right':
                self._robot.turn_right()
                self.logger.info("turn_right()" + "   command: " + command)
                self._robot.hover()
            elif command == 'turn_left':
                self._robot.turn_left()
                self.logger.info("turn_left()" + "   command: " + command)
                self._robot.hover()
         except:
            self.logger.error("NO CONNECTION TO ROBOT!!!! COMMAND IGNORED!!! In time: "+str(time.time()-t))
            ugm_helper.send_status(self.conn, "Couldn't connect to Robot... Command ignored.")
            time.sleep(0.5)

     def robot_takeoff(self):
        try:
            self._robot.takeoff()
            self.logger.info("takeoff()" + "   command: " + 'takeoff')                 
        except:
            self.logger.error("NO CONNECTION TO ROBOT!!!! COMMAND IGNORED!!! In time: "+str(time.time()-t))
            ugm_helper.send_status(self.conn, "Couldn't connect to Robot... Command ignored.")
            time.sleep(0.5)

    def robot_land(self):
        try:
            self._robot.land()
            self.logger.info("land()" + "   command: " + 'land')                 
        except:
            self.logger.error("NO CONNECTION TO ROBOT!!!! COMMAND IGNORED!!! In time: "+str(time.time()-t))
            ugm_helper.send_status(self.conn, "Couldn't connect to Robot... Command ignored.")
            time.sleep(0.5)
    
