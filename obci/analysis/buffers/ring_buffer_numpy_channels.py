#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy
import ring_buffer_impl
class RingBufferNumpyChannels(ring_buffer_impl.RingBufferImpl):
    def _get_normal(self, start, end):
        return self.buffer[:, start:end]

    def _get_concat(self, start, end):
        return numpy.concatenate((self.buffer[:, start:], 
                                  self.buffer[:, :end]),
                                 axis=1)
    
    def _add(self, s):
        for i in range(self.number_of_channels):
            self.buffer[i, self.index] = s.channels[i]
        
    def _init_buffer(self):
        self.buffer = numpy.zeros((self.number_of_channels, self.size), dtype='float')
