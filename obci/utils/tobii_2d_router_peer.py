#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash

import numpy as np


class Tobii2DRouter(ConfiguredMultiplexerServer):
    @log_crash
    def __init__(self, addresses, peer_type):
        super(Tobii2DRouter, self).__init__(addresses=addresses,
                                            type=peer_type)
        self.l_x_ind = int(self.config.get_param("l_x_ind"))
        self.l_y_ind = int(self.config.get_param("l_y_ind"))
        self.r_x_ind = int(self.config.get_param("r_x_ind"))
        self.r_y_ind = int(self.config.get_param("r_y_ind"))
        track = self.config.get_param("track")
        if len(track)==0:
            self.track = [[1, 1], [1, 1]]
        elif track == "right":
            self.track = [[0, 0], [1, 1]]
        elif track == "left":
            self.track = [[1, 1], [0, 0]]
        self.in_mx_signal_type = types.__dict__[self.config.get_param("in_mx_signal_type")]
        self.out_mx_signal_type = types.__dict__[self.config.get_param("out_mx_signal_type")]
        self.ready()

    def get_msg(self, s):
        msg = variables_pb2.Sample2D()
        data= np.array([[s.channels[self.l_x_ind], s.channels[self.l_y_ind]], [s.channels[self.r_x_ind], s.channels[self.r_y_ind]]])*self.track
        data=np.sum(data, axis=0)
        if np.sum(self.track)==4:
            data/=2
        msg.x = 1 - data[0]
        msg.y = data[1]
        msg.timestamp = s.timestamp
        return msg

    def handle_message(self, mxmsg):
        if mxmsg.type == self.in_mx_signal_type:
            v = variables_pb2.SampleVector()
            v.ParseFromString(mxmsg.message)
            for s in v.samples:
                msg = self.get_msg(s)
                self.conn.send_message(
                        message=msg.SerializeToString(),
                        type=self.out_mx_signal_type, flush=True)
                print msg
        self.no_response()

if __name__ == "__main__":
    Tobii2DRouter(settings.MULTIPLEXER_ADDRESSES, peers.SIGNAL_CATCHER).loop()
