#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

import random, time, pickle

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.utils import context as ctx
from obci.configs import settings, variables_pb2
from obci.devices import appliance_helper
from obci.acquisition import acquisition_helper
from obci.analysis.buffers import auto_ring_buffer
from obci.interfaces.bci.ssvep_csp import bci_ssvep_csp_analysis
from obci.interfaces.bci.ssvep_csp import ssvep_csp_helper
from obci.utils import streaming_debug
from obci.utils import tags_helper
from obci.utils.openbci_logging import log_crash

from obci.interfaces.bci.ssvep_pattern import bci_ssvep_pattern_analysis

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.interfaces.bci.ssvep_csp import ssvep_csp_helper

DEBUG = True
class BCISsvepPattern(ConfiguredMultiplexerServer):
    def send_decision(self, dec):
        """Send dec message to the system (probably to LOGIC peer).
        dec is of integer type."""
        self.logger.info("Sending dec message: "+str(dec))
        self._last_dec_time = time.time()
        self.buffer.clear()
        t = time.time()
        tags_helper.send_tag(
            self.conn, t, t,
            "decision",
            {'decision':str(dec)})
        self.conn.send_message(message = str(self.active_field_ids[dec]), type = types.DECISION_MESSAGE, flush=True)
        appliance_helper.send_stop(self.conn)#, self.str_freqs)


    @log_crash
    def __init__(self, addresses):
        #Create a helper object to get configuration from the system
        super(BCISsvepPattern, self).__init__(addresses=addresses,
                                          type=peers.SSVEP_ANALYSIS)

        #get stats from file
        cfg = self._get_csp_config()

        freqs = [int(f) for f in cfg['freq'].split(';')]

        dec_count = int(self.config.get_param('dec_count'))
        active_field_ids = self.config.get_param('active_field_ids')
        self.active_field_ids = [str(f) for f in active_field_ids.split(';')]
        str_freqs = [str(0)] * len(self.get_param('ugm_field_ids').split(';'))
        #str_freqs[1] = str(100) #TODO fix fix fix, useful only for ssvep maze app .....
        for index1, index2 in enumerate(self.active_field_ids):
            str_freqs[int(index2)] = str(freqs[index1])

        self.str_freqs = (';').join(str_freqs)
            
        if len(freqs) != dec_count:
            raise Exception("Configuration inconsistency! logic dec_count is different from number of decisions to-be-sent from obci.analysis (len(freqs))...."+str(len(freqs))+" != "+str(dec_count))

        sampling = int(self.config.get_param('sampling_rate'))
       
        buffer = int(float(self.config.get_param('buffer_len'))*sampling)

        #Create analysis object to analyse data
        self.analysis = self._get_analysis(self.send_decision, freqs, cfg)

        #Initialise round buffer that will supply analysis with data
        #See auto_ring_buffer documentation

        channels_count = len(self.config.get_param('channel_names').split(';'))
        self.buffer = auto_ring_buffer.AutoRingBuffer(
            from_sample=buffer,
            samples_count=buffer,
            every=int(float(self.config.get_param('buffer_every'))*sampling),
            num_of_channels=channels_count,
            ret_func=self.analysis.analyse,
            ret_format=self.config.get_param('buffer_ret_format'),
            copy_on_ret=int(self.config.get_param('buffer_copy_on_ret'))
            )
        self.hold_after_dec = float(self.config.get_param('hold_after_dec'))
        if DEBUG:
            self.debug = streaming_debug.Debug(int(self.config.get_param('sampling_rate')),
                                               self.logger,
                                               int(self.config.get_param('samples_per_packet')))
        self._last_dec_time = time.time() + 5 #sleep 5 first seconds..
        self.ready()
        appliance_helper.send_freqs(self.conn, str_freqs)
        self.logger.info("BCIAnalysisServer init finished!")

    def _get_analysis(self, send_func, freqs, cfg):
        """Fired in __init__ method.
        Return analysis instance object implementing interface:
        - get_requested_configs()
        - set_configs(configs)
        - analyse(data)
        """
        context = ctx.get_new_context()
        context['logger'] = self.logger
        return bci_ssvep_pattern_analysis.BCISsvepPatternAnalysis(
            send_func,
            freqs,
            cfg,
            self.config.get_param('channel_names').split(';'),
            self.config.get_param('channel_gains').split(';'),
            int(self.config.get_param('sampling_rate')),
            context)
    def handle_message(self, mxmsg):
        if self._last_dec_time > 0:
            t = time.time() - self._last_dec_time
            if t > self.hold_after_dec:
                self._last_dec_time = 0
                appliance_helper.send_start(self.conn)#, self.str_freqs)
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

    def _get_csp_config(self):
        return ssvep_csp_helper.get_csp_config(
            self.config.get_param('config_file_path'),
            self.config.get_param('config_file_name'))


if __name__ == "__main__":
    BCISsvepPattern(settings.MULTIPLEXER_ADDRESSES).loop()
