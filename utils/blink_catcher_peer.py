#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

import os.path
import sys

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci_configs import settings, variables_pb2
from utils import tags_helper
from utils import openbci_logging as logger
LOGGER = logger.get_logger("blink_catcher_peer", 'info')

class BlinkCatcher(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(BlinkCatcher, self).__init__(addresses=addresses,
                                          type=peers.BLINK_CATCHER)
        self.blink_duration = float(self.config.get_param("blink_duration"))
        self.ready()

    def handle_message(self, mxmsg):
        if mxmsg.type == types.BLINK_MESSAGE:
            b = variables_pb2.Blink()
            b.ParseFromString(mxmsg.message)
            LOGGER.debug("GOT BLINK: "+str(b.timestamp)+" / "+str(b.index))
            tags_helper.send_tag(self.conn, 
                                 b.timestamp, b.timestamp+self.blink_duration, "blink",
                                 {"index" : b.index})
        self.no_response()



if __name__ == "__main__":
    BlinkCatcher(settings.MULTIPLEXER_ADDRESSES).loop()

