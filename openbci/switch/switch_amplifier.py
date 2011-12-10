#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import settings, variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client

import random, time, configurer


import switch_logging as logger
LOGGER = logger.get_logger("switch_amplifier", "info")




class SwitchAmplifier(object):
    """A simple class to convey data from multiplexer (UGM_UPDATE_MESSAGE)
    to ugm_engine using udp. That level of comminication is needed, as
    pyqt won`t work with multithreading..."""
    def __init__(self, p_addresses):

        LOGGER.info("Start initializin switch amplifier...")
        configurer_ = configurer.Configurer(p_addresses)
        configs = configurer_.get_configs(['SWITCH_TYPE'])
        self.configs = configs
        self.connection = connect_client(type = peers.SWITCH_AMPLIFIER, addresses=p_addresses)
        LOGGER.info("Switch connected!")
        configurer_.set_configs({'PEER_READY':str(peers.SWITCH_AMPLIFIER)}, self.connection)


    def run(self):
        """Method fired by multiplexer. It conveys update message to 
        ugm_engine using udp sockets."""
        while True:
            i = raw_input()
            LOGGER.debug("Send switch...")
            self.connection.send_message(message = "",
                                         type = types.SWITCH_MESSAGE, flush=True)            

if __name__ == "__main__":
    SwitchAmplifier(settings.MULTIPLEXER_ADDRESSES).run()

