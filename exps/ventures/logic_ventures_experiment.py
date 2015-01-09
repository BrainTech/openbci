#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
from obci.acquisition import acquisition_helper
#from obci.gui.ugm import ugm_helper
import maze
import random, time, sys, thread

class LogicVenturesExperiment(ConfiguredMultiplexerServer):
    def __init__(self, addresses, p_type = peers.LOGIC_WII_BOARD):#todo - change peer type
        self._finish = False
        self._addresses = addresses
        super(LogicVenturesExperiment, self).__init__(addresses=addresses, type=p_type)
        self._maze = maze.MazeGame('test')
        self.run_maze_in_thread()
        self.ready()
        
    def run_maze(self):
        self.logger.info("RUN MAZE START")
        self._maze.run()
        self.logger.info("RUN MAZE END")
        self._finish = True

    def run_maze_in_thread(self):
        self.logger.info("RUN MAZE START THREAD ...")
        thread.start_new_thread(self.run_maze, ())

    def handle_message(self, mxmsg):
        if mxmsg.type == types.WII_BOARD_ANALYSIS_RESULTS:#todo - change it to wii analysis message
            msg = variables_pb2.Sample2D()
            msg.ParseFromString(mxmsg.message)
            #self.logger.info("GOT MESSAGE: "+str(msg))
            self._maze.handle_message((msg.x, msg.y))
        else:
            self.logger.warning("Unrecognised message received! Ignore...")
        self.no_response()

        if self._finish:
            self.logger.info("start finish saving")
            acquisition_helper.finish_saving(self._addresses, ['wii'])
            self.logger.info("finish saving ended")
            sys.exit(0)

if __name__ == "__main__":
    LogicVenturesExperiment(settings.MULTIPLEXER_ADDRESSES).loop()

### todo: logic_wii_exp, analysis_wii_exp, maze mutex buffer, mx_rules_update, scenariusz, 

### todo:
# - jak bedzie odpalana sesna? jak definiowany user? jak scenariusze z rownowaga, sway, potem kalibracja?
# - zrobic scenariusze powyzsze, ze sciezkami do odpowiednich plikow i przekazywaniem tego co trzeba
# - modul w pythonie/pygame do rysowania kalibracji
# - polaczenie scenariusza exp z wii boardem
# - filtrowanie i przeplyw danycg driver - analiza - logika

