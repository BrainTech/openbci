#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from multiplexer.multiplexer_constants import peers, types
from obci.configs import settings, variables_pb2
from obci.logic import logic_helper
import time
from obci.utils.openbci_logging import log_crash

from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

class TestServer2(ConfiguredMultiplexerServer):
    @log_crash
    def __init__(self, addresses):
        super(TestServer2, self).__init__(addresses=addresses, type=peers.CONFIGURER)
        self.ready()
        print "RRRRRRRRRRRREADY!!!"
        time.sleep(5)
        logic_helper.restart_scenario(self.conn, self.get_param('transform_to'),
                                        leave_on=['peer1', 'amplifier'],
                                            overwrites=dict(
                                                peer2=['-p', 'text', 'dupa dupa dupa',
                                                     '-p', 'zzz', '12345'],
                                                peer3=['-f', os.path.join('control', 'test', 'custom_peer_b.ini')]
                                                ))


    def handle_message(self, mxmsg):
        # handle something
        self.no_response()


if __name__ == "__main__":
    srv = TestServer2(settings.MULTIPLEXER_ADDRESSES)
    srv.loop()
