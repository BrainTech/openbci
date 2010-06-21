#!/usr/bin/env python

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2

import time
import numpy
import scipy.signal as signal
 
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
        b = list(b)
        a = list(a)

        # reverse a and b for more convinient use
        self.a0 = a[0]
        a = a[1:]
        a.reverse()
        b.reverse()

        self.a = numpy.array(a)
        self.b = numpy.array(b)
        self.len_x = len(b)
        self.len_y = len(a)


        self.last_x = [[0.0]]*channels_num
        self.last_y = [[0.0]]*channels_num
        for i in range(channels_num):
            self.last_x[i] = numpy.array([0.0]*len(b))
            self.last_y[i] = numpy.array([0.0]*len(a))
        self.i = 0

        self.vec = variables_pb2.SampleVector()
        self.time = time.time()
        self.processing_time = 0.0


    def handle_message(self, mxmsg):
        """For every sample computer filtered value and send it further.
        Filter paramteres are on self.a, self.b."""
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
            #self.i = self.i+1
	    self.vec.ParseFromString(mxmsg.message)
            #start_t = time.time()
	    for i, x in enumerate(self.vec.samples):
                for j in range(self.len_x-1): #shift self.last_x[i] to the left
                    self.last_x[i][j] = self.last_x[i][j+1]
                # append x.value to self.last_x
                self.last_x[i][self.len_x-1] = x.value 
                
                # compute a new filtered value
                # Having filter data on slots (self.a, self.b) compute
                # filtered sample as defined on:
                # http://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.lfilter.html#scipy.signal.lfilter
                new_y = (numpy.inner(self.b, self.last_x[i]) - \
                             numpy.inner(self.a, self.last_y[i]))/self.a0

                for j in range(self.len_y-1): #shift self.last_y[i] to the left
                    self.last_y[i][j] = self.last_y[i][j+1]

                #append new filtered value to self.last_y
                self.last_y[i][self.len_y-1] = new_y

                self.vec.samples[i].value = new_y
            #end_t = time.time()
            #self.processing_time = self.processing_time + end_t - start_t
            #if self.i % 128 == 0:
            #    print("OVERAL TIME: "+str(time.time() - self.time))
            #    self.time = time.time()

            #    print("128 samples processing time:"+str(self.processing_time))
            #    self.processing_time = 0.0

            self.conn.send_message(message=self.vec.SerializeToString(), type=types.FILTERED_SIGNAL_MESSAGE, flush=True)

            self.no_response()


if __name__ == "__main__":
    Filter(settings.MULTIPLEXER_ADDRESSES).loop()
