#!/usr/bin/env python
# -*- coding: utf-8 -*-

from obci.drivers.generic import py_amplifier
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash

class PyAmplifierHard(py_amplifier.PyAmplifier):
    @log_crash
    def __init__(self, addresses):
        super(PyAmplifierHard, self).__init__(addresses=addresses, type=peers.AMPLIFIER) #change peer type if want here, do nothing more

    def _manage_params(self):
        super(PyAmplifierHard, self)._manage_params()
        #connect to device ,set config params
        #init some local parameters
    def do_sampling(self):
        samples = []
        while True:
            #collect self.samples_per_packet tuples (sample[list of floats], timestamp[float]) to samples[list]
            msg = self._create_msg(samples)
            mx_msg =  self._create_mx_msg(msg)
            self.send(mx_msg)

if __name__ == "__main__":
    PyAmplifierHard(settings.MULTIPLEXER_ADDRESSES).do_sampling()

