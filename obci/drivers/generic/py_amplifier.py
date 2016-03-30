#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time

from multiplexer.multiplexer_constants import peers, types
from obci.configs import settings, variables_pb2
from obci.control.peer.configured_client import ConfiguredClient
from obci.utils.openbci_logging import log_crash

class PyAmplifier(ConfiguredClient):
    @log_crash
    def __init__(self, addresses, peer_type=peers.AMPLIFIER):
        super(PyAmplifier, self).__init__(addresses=addresses, type=peer_type)
        self._init()

    def _init(self):
        self._manage_params()
        self.ready()

    def _create_msg(self, samples):
        assert(self.samples_per_packet == len(samples))
        v = variables_pb2.SampleVector()
        for sample, ts in samples:
            s = v.samples.add()
            s.channels.extend(sample)
            s.timestamp = ts
        return v

    def _create_mx_msg(self, msg):
            return msg.SerializeToString()

    def _send(self, msg):
        self.conn.send_message(message = msg,
                               type = self.mx_signal_type, flush=True)

    def _manage_params(self):
        self.samples_per_packet = int(self.get_param("samples_per_packet"))        
        self.mx_signal_type = types.AMPLIFIER_SIGNAL_MESSAGE


