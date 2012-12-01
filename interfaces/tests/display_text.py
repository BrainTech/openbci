#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module is responsible for making 

Author: Dawid Laszuk
Contact: laszukdawid@gmail.com
"""

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
import random, time, sys

from obci.interfaces import interfaces_logging as logger
from obci.gui.ugm import ugm_helper

LOGGER = logger.get_logger("text_display", "debug")


class TextDisplay(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(TextDisplay, self).__init__(addresses=addresses,
                                     type=peers.P300_ANALYSIS)        

        self.initConst()
        self.ready()    
    
    def initConst(self):
        self.display_time = float(self.config.get_param("display_time"))
        self.decCount = float(self.config.get_param("dec_count"))
        
        self.dec = -1
        self.last_time = time.time() + 1        
        
        LOGGER.debug("\n"*2)
        LOGGER.debug("Init complete!")
        LOGGER.debug("\n"*2)

    def handle_message(self, mxmsg):

        if mxmsg.type == types.BLINK_MESSAGE:
            LOGGER.debug("\n"*2)
            LOGGER.debug("Received blink message!")
            if self.dec > self.decCount:
                return
            
            LOGGER.debug("\n"*2)
            LOGGER.debug("!(self.dec > self.decCount)")
            
            
            if time.time() - self.last_time < self.display_time:
                return
            LOGGER.debug("\n"*2)
            LOGGER.debug("!(time.time() - self.last_time < self.display_time)")
            
            self.dec += 1
            self.last_time = time.time()
            self.conn.send_message(message = str(self.dec), type = types.DECISION_MESSAGE, flush=True)
            
        self.no_response()

if __name__ == "__main__":
    TextDisplay(settings.MULTIPLEXER_ADDRESSES).loop()
