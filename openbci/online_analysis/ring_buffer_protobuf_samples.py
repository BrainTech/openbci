#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ring_buffer_impl
class RingBufferProtobufSamples(ring_buffer_impl.RingBufferImpl):
    def _init_buffer(self):
        self.buffer = [None]*self.size

    def _get_normal(self, start, end):
        return self.buffer[start:end]

    def _get_concat(self, start, end):
        return self.buffer[start:] + self.buffer[:end]

    def _add(self, s):
        self.buffer[self.index] = s
