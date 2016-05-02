#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Anna Chabuda <anna.chabuda@fuw.edu.pl>
#

import random, time, pickle

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.utils import context as ctx
from obci.configs import settings, variables_pb2
from obci.acquisition import acquisition_helper
from obci.analysis.buffers import auto_ring_buffer
from obci.interfaces.biofeedback import biofeedback_analysis
from obci.utils import streaming_debug
from obci.utils import tags_helper
from obci.utils.openbci_logging import log_crash

DEBUG = False

class BiofeedbackAnalysis(ConfiguredMultiplexerServer):
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
        self.conn.send_message(message = str(dec), type = types.DECISION_MESSAGE, flush=True)

    @log_crash
    def __init__(self, addresses):
        #Create a helper object to get configuration from the system
        super(BiofeedbackAnalysis, self).__init__(addresses=addresses,
                                          type=peers.SSVEP_ANALYSIS)

        #Initialise paramiters...
        sampling = int(self.config.get_param('sampling_rate'))
        buffer = int(self.config.get_param('buffer_len'))*sampling
        self.hold_after_dec = float(self.config.get_param('hold_after_dec'))

        #create analysis object to analyse data
        self.analysis = self._get_analysis(self.send_decision)

        self.fft = int(self.config.get_param("fft"))

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

        if DEBUG:
            self.debug = streaming_debug.Debug(int(self.config.get_param('sampling_rate')),
                                               self.logger,
                                               int(self.config.get_param('samples_per_packet')))
        self._last_dec_time = time.time() + 5 #sleep 5 first seconds..
        self.ready()
        self.logger.info("BiofeedbackAnalysis init finished!")

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

    def _get_analysis(self, send_func):
        """Fired in __init__ method.
        Return analysis instance object implementing interface:
        - get_requested_configs()
        - set_configs(configs)
        - analyse(data)
        """
        context = ctx.get_new_context()
        context['logger'] = self.logger
        return biofeedback_analysis.BiofeedbackAnalysis(
            send_func,
            int(self.config.get_param('sampling_rate')),
            context)
    


if __name__ == "__main__":
    BiofeedbackAnalysis(settings.MULTIPLEXER_ADDRESSES).loop()
