#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash

class Sample2DRouter(ConfiguredMultiplexerServer):
	@log_crash
    def __init__(self, addresses, peer_type):
        super(Sample2DRouter, self).__init__(addresses=addresses,
                                          type=peer_type)
        self.x_ind = int(self.config.get_param("x_ind"))
        self.y_ind = int(self.config.get_param("y_ind"))
        self.in_mx_signal_type = types.__dict__[self.config.get_param("in_mx_signal_type")]
        self.out_mx_signal_type = types.__dict__[self.config.get_param("out_mx_signal_type")]
        self.ready()

    def handle_message(self, mxmsg):
        if mxmsg.type == self.in_mx_signal_type:
            v = variables_pb2.SampleVector()
            v.ParseFromString(mxmsg.message)
            for s in v.samples:
                msg = variables_pb2.Sample2D()
                msg.x = s.channels[self.x_ind]
                msg.y = s.channels[self.y_ind]
                msg.timestamp = s.timestamp
                self.conn.send_message(
                        message=v.SerializeToString(),
                        type=self.out_mx_signal_type, flush=True)
        self.no_response()

