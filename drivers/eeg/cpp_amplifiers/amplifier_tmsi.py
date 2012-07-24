#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from multiplexer.multiplexer_constants import peers, types
from drivers.eeg.binary_driver_wrapper import BinaryDriverWrapper
from drivers import drivers_logging as logger
from obci_configs import settings

LOGGER = logger.get_logger("AmplifierTMSI", "info")

class AmplifierTMSI(BinaryDriverWrapper):
    def __init__(self, addresses):
        super(AmplifierTMSI, self).__init__(addresses=addresses, type=peers.AMPLIFIER_SERVER)

if __name__ == "__main__":
    srv = AmplifierTMSI(settings.MULTIPLEXER_ADDRESSES)
    srv.do_sampling()
