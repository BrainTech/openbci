#!/usr/bin/env python
# -*- coding: utf-8 -*-

from obci.drivers.generic import py_amplifier
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash

MAX_CHANNELS = 8 + 3  # 8 signal channels + 3 aux channels

class PyAmplifierOpenBCI_V3(py_amplifier.PyAmplifier):
    @log_crash
    def __init__(self, addresses):
        super(PyAmplifierHard, self).__init__(addresses=addresses, type=peers.AMPLIFIER) #change peer type if want here, do nothing more

    def _manage_params(self):
        if int(self.get_param("amplifier_online")) == 1:
            self.logger.info("Initializing OpenBCI.com V3 board...")
            try:
                port = self.get_param('port')
                self.board = OpenBCIV3_Board(port, self._samples_callback)
            except Exception as error:
                self.logger.error("{} ABORTING...".format(error))
                sys.exit(1)
            self.logger.info("Connected to OpenBCI.com V3 board...")
        elif int(self.get_param("amplifier_online")) == 0:
            self.logger.info("Initializing OpenBCI.com V3 (DUMMY) board...")
            self.wbb = OpenBCIV3_Board_Dummy(self._samples_callback)
            self.logger.info("Connected to OpenBCI.com V3 (DUMMY) board...")
        else:
            self.logger.error("'amplifier_online' parameter is wrong (possible values: 0, 1) ABORTING...")
            sys.exit(1)

        super(PyAmplifierOpenBCI_V3, self)._manage_params()

        #self.mx_signal_type = types.WII_BOARD_SIGNAL_MESSAGE
        
        active_channels = self.get_param('active_channels').split(';')
        channel_names = self.get_param('channel_names').split(';')
        
        if len(channel_names) > MAX_CHANNELS or len(active_channels) > MAX_CHANNELS:
            self.logger.error("To many channels. ABORTING...")
            sys.exit(1)            
        elif len(channel_names) == len(active_channels):
            self.set_param('channel_gains', ';'.join([str(1.0) for i in channel_names]))
            self.set_param('channel_offsets', ';'.join([str(0.0) for i in channel_names]))
        else:
            self.logger.error("Number of active channels is not equal to the number of channel names!!! ABORTING...")
            sys.exit(1)
        
        self.collected_samples = []
        self.samples_per_packet = int(self.get_param('samples_per_packet'))
        if self.samples_per_packet <= 0:
            self.logger.error("'samples_per_packet' parameter must be > 0. ABORTING...")
            sys.exit(1)

        self.sampling_rate = int(self.get_param('sampling_rate'))
        
        if self.sampling_rate != 250:
            self.logger.error("'sampling_rate' parameter must be set to 250. ABORTING...")
            sys.exit(1)
    
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
