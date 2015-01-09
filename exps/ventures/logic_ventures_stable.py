#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os.path, time
from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2

from obci.acquisition import acquisition_helper

class LogicVenturesStable(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(LogicVenturesStable, self).__init__(addresses=addresses,
                                                type=peers.CLIENT)
        self.ready()
        self.logger.info("start waiting for saving finished")
        acquisition_helper.wait_saving_finished(addresses, ['wii'])
        self.logger.info("saving finished! Start analysis...")
        time.sleep(3)
        sys.exit(0)
    
if __name__ == "__main__":
    LogicVenturesStable(settings.MULTIPLEXER_ADDRESSES).loop()
