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
from analysis.buffers import auto_blink_buffer
from interfaces.bci.p300_csp import bci_p300_csp_analysis
from interfaces.bci.ssvep_csp import ssvep_csp_helper

LOGGER = logger.get_logger("bci_p300_csp")


class BCIP300Csp(ConfiguredMultiplexerServer):
    def send_decision(self, dec):
        """Send dec message to the system (probably to LOGIC peer).
        dec is of integer type."""
        LOGGER.info("Sending dec message: "+str(dec))
        self._last_dec_time = time.time()
        self.buffer.clear()
        self.conn.send_message(message = str(dec), type = types.DECISION_MESSAGE, flush=True)

    def __init__(self, addresses):
        #Create a helper object to get configuration from the system
        super(BCIP300Csp, self).__init__(addresses=addresses,
                                          type=peers.P300_ANALYSIS)

        #get stats from file
        cfg = self._get_csp_config()
        montage_matrix = self._get_montage_matrix(cfg)
            
        #dec_count = int(self.config.get_param('dec_count'))

        #Create analysis object to analyse data 
        self.analysis = self._get_analysis(self.send_decision, cfg, montage_matrix)

        #Initialise round buffer that will supply analysis with data
        #See auto_ring_buffer documentation
        sampling = int(self.config.get_param('sampling_rate'))
        channels_count = len(self.config.get_param('channel_names').split(';'))
        self.buffer = auto_blink_buffer.AutoBlinkBuffer(
            from_blink=0,
            samples_count=int(float(cfg['buffer'])*sampling),
            sampling=sampling,
            num_of_channels=channels_count,
            ret_func=self.analysis.analyse,
            ret_format=self.config.get_param('buffer_ret_format'),
            copy_on_ret=int(self.config.get_param('buffer_copy_on_ret'))
            )
        
        self.hold_after_dec = float(self.config.get_param('hold_after_dec'))
        self._last_dec_time = time.time() + 5 #sleep 5 first seconds..
        self.ready()
        LOGGER.info("BCIAnalysisServer init finished!")

    def handle_message(self, mxmsg):
        if self._last_dec_time > 0:
            t = time.time() - self._last_dec_time
            if t > self.hold_after_dec:
                self._last_dec_time = 0
            else:
                self.no_response()
                return

        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
	    l_msg = variables_pb2.SampleVector()
            l_msg.ParseFromString(mxmsg.message)
            #Supply buffer with sample data, the buffer will fire its
            #ret_func (that we defined as self.analysis.analyse) every 'every' samples
            self.buffer.handle_sample_vect(l_msg)
        elif mxmsg.type == types.BLINK_MESSAGE:
	    l_msg = variables_pb2.Blink()
            l_msg.ParseFromString(mxmsg.message)
            self.buffer.handle_blink(l_msg)
            
        self.no_response()

    def _get_analysis(self, send_func, cfg, montage_matrix):
        """Fired in __init__ method.
        Return analysis instance object implementing interface:
        - get_requested_configs()
        - set_configs(configs)
        - analyse(data)
        """
        return bci_p300_csp_analysis.BCIP300CspAnalysis(
            send_func,
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
    BCIP300Csp(settings.MULTIPLEXER_ADDRESSES).loop()
