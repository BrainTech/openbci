#!/usr/bin/env python
# -*- coding: utf-8 -*-

from obci.drivers.generic import py_amplifier
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash

MAX_CHANNELS = 8 + 3  # 8 signal channels + 3 auxiliary channels

class PyAmplifierOpenBCI_V3(py_amplifier.PyAmplifier):
    @log_crash
    def __init__(self, addresses):
        super(PyAmplifierOpenBCI_V3, self).__init__(addresses=addresses, type=peers.AMPLIFIER)

    def _init(self):
        self._manage_params()
        self.board.start_streaming(self._samples_callback)        
        self.ready()

    def _manage_params(self):
        super(PyAmplifierOpenBCI_V3, self)._manage_params()
        
        active_channels = map(int, self.get_param('active_channels').split(';'))
        channel_names = self.get_param('channel_names').split(';')
        
        if len(channel_names) > MAX_CHANNELS or len(active_channels) > MAX_CHANNELS:
            self.logger.error("To many channels specified. ABORTING...")
            sys.exit(1)            
        
        if len(channel_names) != len(active_channels):
            self.logger.error("Number of active channels is not equal to the number of channel names!!! ABORTING...")
            sys.exit(1)

        self.set_param('channel_gains', ';'.join([str(1.0) for i in channel_names]))
        self.set_param('channel_offsets', ';'.join([str(0.0) for i in channel_names]))
        
        self.collected_samples = []
        if self.samples_per_packet <= 0:
            self.logger.error("'samples_per_packet' parameter must be > 0. ABORTING...")
            sys.exit(1)

        self.sampling_rate = int(self.get_param('sampling_rate'))
        if self.sampling_rate != 250:
            self.logger.error("'sampling_rate' parameter must be set to 250. ABORTING...")
            sys.exit(1)

        if int(self.get_param("amplifier_online")) == 1:
            self.logger.info("Initializing OpenBCI.com V3 board...")
            try:
                self.board = OpenBCIV3_Board()
            except Exception as error:
                self.logger.error("{} ABORTING...".format(error))
                sys.exit(1)
            self.logger.info("Connected to OpenBCI.com V3 board...")
        elif int(self.get_param("amplifier_online")) == 0:
            self.logger.info("Initializing OpenBCI.com V3 (DUMMY) board...")
            self.board = OpenBCIV3_Board_Dummy()
            self.logger.info("Connected to OpenBCI.com V3 (DUMMY) board...")
        else:
            self.logger.error("'amplifier_online' parameter must be 0 or 1. ABORTING...")
            sys.exit(1)

        port = self.get_param('port')
        
        self.board.set_param(active_channels, 
                             self.sampling_rate, 
                             port)

    
    def _samples_callback(self, params):
        samples, timestamp = params[0], params[1]
        self.collected_samples.append((samples, timestamp))
        if len(self.collected_samples) == self.samples_per_packet:
            v = variables_pb2.SampleVector()
            for sample, ts in self.collected_samples:
                s = v.samples.add()
                s.channels.extend(sample)
                s.timestamp = ts
            self._send(self._create_mx_msg(v))
            self.collected_samples = []

if __name__ == "__main__":
    PyAmplifierHard(settings.MULTIPLEXER_ADDRESSES).do_sampling()
