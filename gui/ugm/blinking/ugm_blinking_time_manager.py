#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>


import random
class UgmBlinkingTimeManager(object):
    """Provides time of break between two blinks as random float from range[BLINK_MIN_BREAK;BLINK_MAX_BREAK]"""
    def get_requested_configs(self):
        return ['BLINK_MIN_BREAK', # Time (in secs) between two blinks will be generated as float from range[BLINK_MIN_BREAK;BLINK_MAX_BREAK]
                'BLINK_MAX_BREAK']

    def set_configs(self, configs):
        self._min_break = float(configs['BLINK_MIN_BREAK'])
        self._max_break_span = float(configs['BLINK_MAX_BREAK']) - self._min_break
        assert(self._max_break_span >= 0)

    def get_time(self):
        if self._max_break_span == 0:
            return self._min_break
        else:
            return self._min_break + random.random()*self._max_break_span

    def reset(self):
        pass

