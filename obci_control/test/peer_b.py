#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2

import peer.peer_config_control
import common.config_message as cmsg

class TestServer(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(TestServer, self).__init__(addresses=addresses, type=peers.ETR_SERVER)
        self.config = None

    def configure(self):
        self.config = peer.peer_config_control.PeerConfigControl(self)
        self.config.initialize_config(self.conn)

        self.config.send_peer_ready(self.conn)
        self.config.synchronize_ready(self.conn)


    def handle_message(self, mxmsg):
        # handle something
        self.no_response()

if __name__ == "__main__":
    srv = TestServer(settings.MULTIPLEXER_ADDRESSES)
    srv.configure()
    srv.loop()