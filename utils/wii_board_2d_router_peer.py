#!/usr/bin/env python
# -*- coding: utf-8 -*-

from obci.configs import settings

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash

from obci.analysis.balance import wii_utils

class WiiBoard2DRouter(ConfiguredMultiplexerServer):
    @log_crash
    def __init__(self, addresses, peer_type):
        super(WiiBoard2DRouter, self).__init__(addresses=addresses, type=peer_type)
        self.in_mx_signal_type = types.__dict__[self.config.get_param("in_mx_signal_type")]
        self.out_mx_signal_type = types.__dict__[self.config.get_param("out_mx_signal_type")]
        self.ready()
    def handle_message(self, mxmsg):
        if mxmsg.type == self.in_mx_signal_type:
            v = variables_pb2.SampleVector()
            v.ParseFromString(mxmsg.message)
            for s in v.samples:
                msg = variables_pb2.Sample2D()
                x, y = wii_utils.get_x_y(s.channels[0], s.channels[1], s.channels[2], s.channels[3])
                msg.x = 0.5 - x*0.5
                msg.y = 0.5 - y*0.5
                msg.timestamp = s.timestamp
                self.conn.send_message(
                        message=msg.SerializeToString(),
                        type=self.out_mx_signal_type, flush=True)
        self.no_response()
if __name__ == "__main__":
    WiiBoard2DRouter(settings.MULTIPLEXER_ADDRESSES, peers.WII_BOARD_SIGNAL_CATCHER).loop()
