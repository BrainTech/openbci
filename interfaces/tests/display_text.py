#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module is responsible for making 

Author: Dawid Laszuk
Contact: laszukdawid@gmail.com
"""

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci_configs import settings, variables_pb2
import random, time, sys

from interfaces import interfaces_logging as logger
from gui.ugm import ugm_helper

LOGGER = logger.get_logger("text_display", "debug")


class TextDisplay(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(TextDisplay, self).__init__(addresses=addresses,
                                     type=peers.RESULTS_ANALYSIS)        

        self.initConst()
        self.ready()    
    
    def initConst(self):
        self.display_time = float(self.config.get_param("display_time"))
        self.decCount = float(self.config.get_param("dec_count"))
        
        self.dec = -1
        self.last_time = time.time() + 1        

    def handle_message(self, mxmsg):

        if mxmsg.type == types.BLINK_MESSAGE:
            if self.dec > self.decCount:
                return
                
            if time.time() - self.last_time < self.display_time:
                return
            
            self.dec += 1
            self.conn.send_message(message = str(self.dec), type = types.DECISION_MESSAGE, flush=True)
            
        self.no_response()

if __name__ == "__main__":
    TextDisplay(settings.MULTIPLEXER_ADDRESSES).loop()
