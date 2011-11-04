#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2

import peer.peer_config_control

class TestServer2(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(TestServer2, self).__init__(addresses=addresses, type=peers.ETR_SERVER)
        self.config = peer.peer_config_control.PeerControl(self)

    def initialize_config(self):
        self.config.initialize_config()



    def handle_message(self, mxmsg):
        if mxmsg.type == types.ETR_SIGNAL_MESSAGE:
	       pass
        self.no_response()



if __name__ == "__main__":
    srv = TestServer2(settings.MULTIPLEXER_ADDRESSES)
    srv.initialize_config()
    srv.loop()