#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import settings, variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client

import random, time, configurer

from experiment_builder import keystroke
import switch_logging as logger
LOGGER = logger.get_logger("switch_amplifier", "info")




class SwitchAmplifier(object):
    """A simple class to convey data from multiplexer (UGM_UPDATE_MESSAGE)
    to ugm_engine using udp. That level of comminication is needed, as
    pyqt won`t work with multithreading..."""
    def __init__(self, p_addresses):

        LOGGER.info("Start initializin switch amplifier...")
        configurer_ = configurer.Configurer(p_addresses)
        configs = configurer_.get_configs(['SWITCH_KEY_CODE'])
        self.configs = configs
        self.connection = connect_client(type = peers.SWITCH_AMPLIFIER, addresses=p_addresses)
        LOGGER.info("Switch connected!")
        configurer_.set_configs({'PEER_READY':str(peers.SWITCH_AMPLIFIER)}, self.connection)


    def run(self):
        while True:
            i = keystroke.wait([self.configs['SWITCH_KEY_CODE']])
            if i == 'Escape':
                LOGGER.debug("Got Escape button, finish switch amplifier...")
                break
            LOGGER.debug("Send switch...")
            self.connection.send_message(message = "",
                                         type = types.SWITCH_MESSAGE, flush=True)            
            
if __name__ == "__main__":
    SwitchAmplifier(settings.MULTIPLEXER_ADDRESSES).run()

