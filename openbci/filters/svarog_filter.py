#!/usr/bin/env python

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2

import time
import pylab
import numpy
import scipy.signal as signal
 

def mati_lfilter(b, a, x, y):
    ret = 0.0
    for i, b_value in enumerate(b):
        ret = ret + b_value*x[-1-i]
    for i, a_value in enumerate(a[1:]):
        ret = ret - a_value*y[-1-i]
    return ret/a[0]
        

class Filter(BaseMultiplexerServer):
    def __init__(self, addresses):
        """Get data from hashtable and create filter - butter by now."""
        super(Filter, self).__init__(addresses=addresses, type=peers.FILTER)
        channels_num = int(
            self.conn.query(message = "NumOfChannels", 
                            type = types.DICT_GET_REQUEST_MESSAGE, 
                            timeout = 1).message)
        sampling = float(
            self.conn.query(message = "SamplingRate", 
                            type = types.DICT_GET_REQUEST_MESSAGE, 
                            timeout = 1).message)
        
        f_level = int(
            self.conn.query(message = "FilterLevel", 
                                  type = types.DICT_GET_REQUEST_MESSAGE, 
                                  timeout = 1).message)
        down = int(
            self.conn.query(message = "FilterDown", 
                            type = types.DICT_GET_REQUEST_MESSAGE, 
                            timeout = 1).message)
        up = int(
            self.conn.query(message = "FilterUp", 
                            type = types.DICT_GET_REQUEST_MESSAGE, 
                            timeout = 1).message)
        f_band = self.conn.query(message = "FilterBand", 
                                 type = types.DICT_GET_REQUEST_MESSAGE, 
                                 timeout = 1).message

        b,a = signal.butter(f_level,[down/sampling, up/sampling],btype=f_band)
        self.b = b
        self.a = a
        f_size = len(self.a)+1
        self.last_x = [[0.0]]*channels_num
        self.last_y = [[0.0]]*channels_num
        for i in range(channels_num):
            self.last_x[i] = [0.0]*f_size
            self.last_y[i] = [0.0]*f_size
        self.i = 0
        self.vec = variables_pb2.SampleVector()
        #self.time = time.time()

    def _get_lfiltered_sample(self, x, y):
        """Having filter data on slots (self.a, self.b) computer and return 
        filtered sample as defined on:
        http://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter.html#scipy.signal.lfilter
        Parameters:
        x - a vector of few last raw data
        y - a vetore of few last filtered data
        TO be precise: if we we are trying to generate n-th filtered sample
        the last element in x is n-th raw sample
        the last element in y is n-1 -th filtered sample.
        """
        ret = 0.0
        for i, b_value in enumerate(self.b):
            ret = ret + b_value*x[-1-i]
        for i, a_value in enumerate(self.a[1:]):
            ret = ret - a_value*y[-1-i]
        return ret/self.a[0]
        

    def handle_message(self, mxmsg):
        """For every sample computer filtered value and send it further.
        Filter paramteres are on self.a, self.b."""
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
            #self.i = self.i+1
	    self.vec.ParseFromString(mxmsg.message)
	    for i, x in enumerate(self.vec.samples):
                self.last_x[i].append(x.value)
                new_y = self._get_lfiltered_sample(self.last_x[i], 
                                                   self.last_y[i])
                self.last_y[i].append(new_y)
                # truncate stored last values so that it keeps its size
                self.last_y[i] = self.last_y[i][1:] 
                self.last_x[i] = self.last_x[i][1:]
                self.vec.samples[i].value = new_y
            #if self.i % 128 == 0:
            #    print(time.time() - self.time)
            #    self.time = time.time()

            self.conn.send_message(message=self.vec.SerializeToString(), type=types.FILTERED_SIGNAL_MESSAGE, flush=True)

            self.no_response()


if __name__ == "__main__":
    Filter(settings.MULTIPLEXER_ADDRESSES).loop()
