#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

import random, time, pickle

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from configs import settings, variables_pb2
from devices import appliance_helper
from acquisition import acquisition_helper
from interfaces import interfaces_logging as logger
from analysis.buffers import auto_ring_buffer
from interfaces.bci.ssvep_csp import bci_ssvep_csp_analysis
from interfaces.bci.ssvep_csp import ssvep_csp_helper
from utils import streaming_debug

LOGGER = logger.get_logger("bci_ssve_csp", "info")
DEBUG = False


class BCISsvepCsp(ConfiguredMultiplexerServer):
    def send_decision(self, dec):
        """Send dec message to the system (probably to LOGIC peer).
        dec is of integer type."""
        LOGGER.info("Sending dec message: "+str(dec))
        self._last_dec_time = time.time()
        self.buffer.clear()
        self.conn.send_message(message = str(dec), type = types.DECISION_MESSAGE, flush=True)

    def __init__(self, addresses):
        #Create a helper object to get configuration from the system
        super(BCISsvepCsp, self).__init__(addresses=addresses,
                                          type=peers.SSVEP_ANALYSIS)

        #get stats from file
        cfg = self._get_csp_config()
        montage_matrix = self._get_montage_matrix(cfg)
            

        freqs = [int(f) for f in cfg['freqs'].split(';')]
        str_freqs = [str(f) for f in freqs]
        dec_count = int(self.config.get_param('dec_count'))
        if len(freqs) != dec_count:
            raise Exception("Configuration inconsistency! logic dec_count is different from number of decisions to-be-sent from analysis (len(freqs))...."+str(len(freqs))+" != "+str(dec_count))

        #Create analysis object to analyse data 
        self.analysis = self._get_analysis(self.send_decision, freqs, cfg, montage_matrix)

        #Initialise round buffer that will supply analysis with data
        #See auto_ring_buffer documentation
        sampling = int(self.config.get_param('sampling_rate'))
        channels_count = len(self.config.get_param('channel_names').split(';'))
        self.buffer = auto_ring_buffer.AutoRingBuffer(
            from_sample=int(float(cfg['buffer'])*sampling),
            samples_count=int(float(cfg['buffer'])*sampling),
            every=int(float(self.config.get_param('buffer_every'))*sampling),
            num_of_channels=channels_count,
            ret_func=self.analysis.analyse,
            ret_format=self.config.get_param('buffer_ret_format'),
            copy_on_ret=int(self.config.get_param('buffer_copy_on_ret'))
            )
        
        self.hold_after_dec = float(self.config.get_param('hold_after_dec'))
        if DEBUG:
            self.debug = streaming_debug.Debug(int(self.config.get_param('sampling_rate')),
                                               LOGGER,
                                               int(self.config.get_param('samples_per_packet')))
        self._last_dec_time = time.time() + 5 #sleep 5 first seconds..
        self.ready()
        appliance_helper.send_freqs(self.conn, str_freqs)
        LOGGER.info("BCIAnalysisServer init finished!")

    def handle_message(self, mxmsg):
        if self._last_dec_time > 0:
            t = time.time() - self._last_dec_time
            if t > self.hold_after_dec:
                self._last_dec_time = 0
            else:
                if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE and DEBUG:
                    self.debug.next_sample()
                self.no_response()
                return

        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
	    l_msg = variables_pb2.SampleVector()
            l_msg.ParseFromString(mxmsg.message)
            #Supply buffer with sample data, the buffer will fire its
            #ret_func (that we defined as self.analysis.analyse) every 'every' samples
            self.buffer.handle_sample_vect(l_msg)
            if DEBUG:
                self.debug.next_sample()
        self.no_response()

    def _get_analysis(self, send_func, freqs, cfg, montage_matrix):
        """Fired in __init__ method.
        Return analysis instance object implementing interface:
        - get_requested_configs()
        - set_configs(configs)
        - analyse(data)
        """
        return bci_ssvep_csp_analysis.BCISsvepCspAnalysis(
            send_func,
            freqs,
            cfg,
            montage_matrix,
            int(self.config.get_param('sampling_rate')))


    def _get_csp_config(self):
        return ssvep_csp_helper.get_csp_config(
            self.config.get_param('config_file_path'),
            self.config.get_param('config_file_name'))

    def _get_montage_matrix(self, cfg):
        return ssvep_csp_helper.get_montage_matrix(
            self.config.get_param('channel_names').split(';'),
            cfg['use_channels'].split(';'),
            cfg['montage'],
            cfg['montage_channels'].split(';'))
        

if __name__ == "__main__":
    BCISsvepCsp(settings.MULTIPLEXER_ADDRESSES).loop()
