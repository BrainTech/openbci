#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci_configs import settings, variables_pb2

from peer.configured_multiplexer_server import ConfiguredMultiplexerServer

print "dupadupadupadupa"

class TestServer(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(TestServer, self).__init__(addresses=addresses, type=peers.CONFIGURER)
        self.ready()



    def handle_message(self, mxmsg):
        # handle something
        self.no_response()

if __name__ == "__main__":
    srv = TestServer(settings.MULTIPLEXER_ADDRESSES)
    srv.loop()