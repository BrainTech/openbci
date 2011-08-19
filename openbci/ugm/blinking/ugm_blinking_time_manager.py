#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
class UgmBlinkingTimeManager(object):
    def get_requested_configs(self):
        return ['BLINK_MIN_BREAK', 'BLINK_MAX_BREAK']

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

