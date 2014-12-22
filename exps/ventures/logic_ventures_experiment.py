#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
#from obci.gui.ugm import ugm_helper
#from maze import maze
import random, time, sys, thread

class LogicVenturesExperiment(ConfiguredMultiplexerServer):
    def __init__(self, addresses, p_type = peers.LOGIC_WII_BOARD):#todo - change peer type
        super(LogicVenturesExperiment, self).__init__(addresses=addresses, type=p_type)
        #self.run_maze_in_thread()

    def run_maze(self):
        self.logger.info("RUN MAZE START")
        a = maze.MazeGame('test')
        self.a = a
        a.run()
        self.logger.info("RUN MAZE END")

    def run_maze_in_thread(self):
        self.logger.info("RUN MAZE START THREAD ...")
        thread.start_new_thread(self.run_maze, ())

    def handle_message(self, mxmsg):
        if mxmsg.type == types.WII_BOARD_ANALYSIS_RESULTS:#todo - change it to wii analysis message
            l_msg = variables_pb2.Sample2D()
            l_msg.ParseFromString(mxmsg.message)
            self.logger.info("GOT MESSAGE: "+str(l_msg))
            #dec, ugm = self.handle_etr_message(l_msg)
            #if dec >= 0:
            #    self.logger.debug("Sending dec message...")
            #    self.conn.send_message(message = str(dec), type = types.DECISION_MESSAGE, flush=True)
            #elif ugm is not None:
            #    self.logger.debug("Sending ugm message...")
            #    ugm_helper.send_config(self.conn, ugm, 1)
            #else:
            #    self.logger.info("Got notihing from manager...")
            #self.a.got_msg(l_msg, self.logger)

        self.no_response()

if __name__ == "__main__":
    LogicVenturesExperiment(settings.MULTIPLEXER_ADDRESSES).loop()

### todo: logic_wii_exp, analysis_wii_exp, maze mutex buffer, mx_rules_update, scenariusz, 
