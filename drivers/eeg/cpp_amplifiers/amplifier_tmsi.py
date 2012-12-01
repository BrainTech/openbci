#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from multiplexer.multiplexer_constants import peers, types
from obci.drivers.eeg.binary_driver_wrapper import BinaryDriverWrapper
from obci.configs import settings

class AmplifierTMSI(BinaryDriverWrapper):
    def __init__(self, addresses):
        super(AmplifierTMSI, self).__init__(addresses=addresses, type=peers.AMPLIFIER_SERVER)

if __name__ == "__main__":
    srv = AmplifierTMSI(settings.MULTIPLEXER_ADDRESSES)
    srv.do_sampling()
