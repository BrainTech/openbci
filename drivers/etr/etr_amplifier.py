#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_client import ConfiguredClient

from obci_configs import settings, variables_pb2

class EtrAmplifier(ConfiguredClient):
    """A simple class to convey data from multiplexer (UGM_UPDATE_MESSAGE)
    to ugm_engine using udp. That level of comminication is needed, as
    pyqt won`t work with multithreading..."""
    def __init__(self, addresses):
        super(EtrAmplifier, self).__init__(addresses=addresses, type=peers.ETR_AMPLIFIER)
        self.logger.info("Start initializin etr amplifier...")

    def process_message(self, msg):
        self.logger.debug("ETR sending message ... x = "+str(msg.x) + ", y = "+str(msg.y))
        self.conn.send_message(message = msg.SerializeToString(), 
                               type = types.ETR_SIGNAL_MESSAGE, flush=True)
    
    def run(self):
        raise Exception("To be subclassed!!!")
