#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import time, numpy
import scipy.signal as ss
from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
from obci.analysis.buffers import auto_ring_buffer
from obci.interfaces import interfaces_logging as logger

class BCIalpha(ConfiguredMultiplexerServer):
    def send_decision(self, dec):
        #self.buffer.clear()
        self.conn.send_message(message = str(dec), type = types.DECISION_MESSAGE, flush=True)
        
    def __init__(self, addresses):
        super(BCIalpha, self).__init__(addresses=addresses,
                                          type=peers.SSVEP_ANALYSIS)

        self.treshold = float(self.config.get_param('treshold'))
        self.fs = float(self.config.get_param('sampling_rate'))

        self.buffer = auto_ring_buffer.AutoRingBuffer(
            from_sample=int(float(self.config.get_param('buffer_len'))*self.fs),
            samples_count=int(float(self.config.get_param('buffer_len'))*self.fs),
            every=int(float(self.config.get_param('buffer_every'))*self.fs),
            num_of_channels=len(self.config.get_param('active_channels').split(';')),
            ret_func=self.analyse,
            ret_format=self.config.get_param('buffer_ret_format'),
            copy_on_ret=int(self.config.get_param('buffer_copy_on_ret'))
            )
        self.ready()
 
    def handle_message(self, mxmsg):
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
            l_vect = variables_pb2.SampleVector()
            l_vect.ParseFromString(mxmsg.message)
            self.buffer.handle_sample_vect(l_vect)
        else:
            pass
        self.no_response()
    def analyse(self, data):

        signal = data[0]
        [a,b]=ss.butter(2, 13/(self.fs*0.5), btype = 'lowpass')
        [c,d] = ss.butter(2, 8/(self.fs*0.5), btype = 'highpass')
        signal = ss.filtfilt(c,d,signal)
        signal = ss.filtfilt(a,b,signal)
        E = numpy.sum((signal/signal.shape[0])**2)
        print '********************************************************\n{}\n********************************************************'.format(E)
        if E > self.treshold:
            dec = 1
        else:
            dec = 0
        self.send_decision(dec)
        return 0

if __name__ == "__main__":
    BCIalpha(settings.MULTIPLEXER_ADDRESSES).loop()
