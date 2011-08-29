#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import sequence_provider
class DummyProvider(object):
    def get_value(self):
        return -1

class UgmBlinkingCountManager(object):
    """For how long should blinker blink? This class provides rules for that. 
    It returns an int indicating number of blinks to 'stop blinking'.
    Blinking is stopped until blinker receives message 'start_blinking'"""
    def get_requested_configs(self):
        return ['BLINK_COUNT_TYPE', # An algorithm generating counts. Possible values:
                    # INF - always returns -1 (should indicate infinity - blink forever)
                    # RANDOM - random values from range [0;BLINK_ID_COUNT]
                    # SEQUENTIAL - sequental values from range [0;BLINK_ID_COUNT]
                    # RANDOM_SEQUENTIAL - random, but not repeated values from range [0;BLINK_ID_COUNT]. Eg. for [0,1,2,3] we`ll get
                    # sth like 0 2 3 1  2 3 0 1  3 1 0 2  0 2 1 3 .... 

                # blink counts will be genereated from range [BLINK_COUNT_MIN;BLINK_COUNT_MAX]
                'BLINK_COUNT_MIN', 
                'BLINK_COUNT_MAX']

    def set_configs(self, configs):
        self._type = configs['BLINK_COUNT_TYPE']
        self._start = int(configs['BLINK_COUNT_MIN'])
        self._count = int(configs['BLINK_COUNT_MAX']) - self._start
        assert(self._start >= 0)
        assert(self._count >= 0)
        self.reset()

    def reset(self):
        if self._type != "INF":
            self._mgr = sequence_provider.PROVIDERS[self._type](
                self._start,
                self._count
                )
        else:
            self._mgr = DummyProvider()

    def get_count(self):
        return self._mgr.get_value()
