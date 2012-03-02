#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from configs import settings, variables_pb2
from logic import logic_helper
import time


from peer.configured_multiplexer_server import ConfiguredMultiplexerServer

class TestServer2(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(TestServer2, self).__init__(addresses=addresses, type=peers.CONFIGURER)
        self.ready()
        print "RRRRRRRRRRRREADY!!!"
        time.sleep(2)
        logic_helper.restart_scenario(self.conn, "scenarios/morph_test_b.ini", 
        							leave_on=['peer1', 'amplifier'],
        							overwrites=dict(
        											peer2=['-p', 'text', 'dupa dupa dupa',
        													'-p', 'zzz', '12345'],
        											peer3=['-f', 'obci_control/test/custom_peer_b.ini']
        											))


    def handle_message(self, mxmsg):
        # handle something
        self.no_response()


if __name__ == "__main__":
    srv = TestServer2(settings.MULTIPLEXER_ADDRESSES)
    srv.loop()
