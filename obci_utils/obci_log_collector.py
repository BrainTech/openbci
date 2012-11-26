#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq


from multiplexer.multiplexer_constants import peers, types
# from multiplexer.clients import BaseMultiplexerServer
from peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci_configs import settings

from common.message import send_msg, recv_msg

class OBCILogCollector(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(OBCILogCollector, self).__init__(addresses=addresses, 
                                            type=peers.OBCI_LOG_COLLECTOR)   
        self.ctx = zmq.Context()
        self.forwarder = self.ctx.socket(zmq.PUSH)
        self.forwarder.connect(self.get_param('log_destination_addr'))
        self.ready()

    def handle_message(self, mxmsg):
        if mxmsg.type == types.OBCI_LOG_MESSAGE:
            send_msg(self.forwarder, mxmsg.message)

if __name__ == '__main__':
    OBCILogCollector(settings.MULTIPLEXER_ADDRESSES).loop()
