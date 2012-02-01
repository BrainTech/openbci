#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random, time, pickle

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from configs import settings, variables_pb2
from acquisition import acquisition_helper
from interfaces import interfaces_logging as logger
from analysis.buffers import auto_ring_buffer
from interfaces.bci.ssvep_csp import bci_ssvep_csp_analysis
#FFFfrom etr import etr_ugm_manager

LOGGER = logger.get_logger("bci_ssve_csp")


class BCISsvepCsp(ConfiguredMultiplexerServer):
    def send_decision(self, dec):
        """Send dec message to the system (probably to LOGIC peer).
        dec is of integer type."""
        LOGGER.info("Sending dec message: "+str(dec))
        
        self._last_dec_time = time.time()
        self._last_dec = dec
        self.buffer.clear()
        self.conn.send_message(message = str(dec), type = types.DECISION_MESSAGE, flush=True)

    def __init__(self, addresses):
        #Create a helper object to get configuration from the system
        super(BCISsvepCsp, self).__init__(addresses=addresses,
                                          type=peers.SSVEP_ANALYSIS)

                #get stats from file
        cfg = self._get_csp_config()

        freqs = [float(f) for f in cfg['freqs'].split(';')]
        dec_count = int(self.config.get_param('dec_count'))
        if len(freqs) != dec_count:
            raise Exception("Configuration inconsistency! logic dec_count is different from number of decisions to-be-sent from analysis (len(freqs))...."+str(len(freqs))+" != "+str(dec_count))

        #Create analysis object to analyse data 
        self.analysis = self._get_analysis(self.send_decision, freqs, cfg)

        #FFFself.feed_manager = etr_ugm_manager.EtrUgmManager()
        #feed manager 
        #FFFself.feed_manager.set_configs(configs)

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
        self._last_dec_time = time.time() + 5 #sleep 5 first seconds..
        self._last_dec = 0

        self.ready()
        LOGGER.info("BCIAnalysisServer init finished!")

    def handle_message(self, mxmsg):
        if self._last_dec_time > 0:
            t = time.time() - self._last_dec_time
            """if t > self.hold_after_dec:
                #LOGGER.info("FEED-----: "+str([0]*8))
                self._last_dec_time = 0
                feeds = self.feed_manager.get_ugm_field_updates([0]*8)
                l_ugm_msg = variables_pb2.UgmUpdate()
                l_ugm_msg.type = 1
                l_ugm_msg.value = feeds
                self.conn.send_message(
                    message = l_ugm_msg.SerializeToString(), 
                    type=types.UGM_UPDATE_MESSAGE, flush=True)

            else:
                #LOGGER.info("Holding: "+str(t))
                #LOGGER.info("FEED: "+str([1-(t/self.hold_after_dec)]*8))
                f = [0]*8
                f[self._last_dec] = 1-(t/self.hold_after_dec)
                #f = [1-(t/self.hold_after_dec)]*8
                feeds = self.feed_manager.get_ugm_field_updates(f)

                l_ugm_msg = variables_pb2.UgmUpdate()
                l_ugm_msg.type = 1
                l_ugm_msg.value = feeds
                self.conn.send_message(
                    message = l_ugm_msg.SerializeToString(), 
                    type=types.UGM_UPDATE_MESSAGE, flush=True)

                self.no_response()
                return"""
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
	    l_msg = variables_pb2.SampleVector()
            l_msg.ParseFromString(mxmsg.message)
            #Supply buffer with sample data, the buffer will fire its
            #ret_func (that we defined as self.analysis.analyse) every 'every' samples
            self.buffer.handle_sample_vect(l_msg)
        self.no_response()

    def _get_analysis(self, send_func, freqs, cfg):
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
            int(self.config.get_param('sampling_rate')))

    def _get_csp_config(self):
        file_name = acquisition_helper.get_file_path(
        self.config.get_param('config_file_path'),
        self.config.get_param('config_file_name'))
        csp_file = file_name+'.csp'
        f = open(csp_file, 'r')
        d = pickle.load(f)
        f.close()
        LOGGER.info("Got csp config:")
        LOGGER.info(str(d))
        return d

                                                          

if __name__ == "__main__":
    BCISsvepCsp(settings.MULTIPLEXER_ADDRESSES).loop()
