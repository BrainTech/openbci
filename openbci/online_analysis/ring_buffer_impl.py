#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
class RingBufferImpl(object):
    def __init__(self, size, number_of_channels, copy_on_ret):
        self.size = int(size)
        self.number_of_channels = int(number_of_channels)
        self.copy_on_ret = bool(copy_on_ret)
        self.clear()

    def clear(self):
        self.is_full = False
        self.index = 0
        self._init_buffer()        

    def add(self, s):
        self._add(s)
        if not self.is_full and self.index == self.size-1:
            self.is_full = True
        self.index = (self.index + 1) % self.size

    def get(self, start, length):
        if not self.is_full:
            d = self._get_normal(start, start+length)
        else:
            if self.index + start + length <= self.size:
                d = self._get_normal(self.index+start, self.index+start+length)
            else:
                d = self._get_concat(self.index+start, length-(self.size - (self.index + start)))

        if self.copy_on_ret:
            return copy.deepcopy(d)
        else:
            return d


    def _get_normal(self, start, end):
        raise Exception("To be implemented!")

    def _get_concat(self, start, end):
        raise Exception("To be implemented!")

    def _add(self, s):
        raise Exception("To be implemented!")

    def _init_buffer(self):
        raise Exception("To be implemented!")

        

