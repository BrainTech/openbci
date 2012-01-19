#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from multiplexer.multiplexer_constants import peers, types
from openbci.amplifiers.binary_driver_wrapper import BinaryDriverWrapper
from openbci.core import  core_logging as logger
import settings


LOGGER = logger.get_logger("AmplifierTMSI", "info")

class AmplifierTMSI(BinaryDriverWrapper):
    def __init__(self, addresses):
        super(AmplifierTMSI, self).__init__(addresses=addresses, type=peers.ETR_SERVER)



if __name__ == "__main__":

    srv = AmplifierTMSI(settings.MULTIPLEXER_ADDRESSES)
    srv.do_sampling()