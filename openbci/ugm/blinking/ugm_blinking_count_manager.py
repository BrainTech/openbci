#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sequence_provider
class UgmBlinkingCountManager(object):
    def get_requested_configs(self):
        return ['BLINK_COUNT_TYPE', 'BLINK_COUNT_MIN', 'BLINK_COUNT_MAX']

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

    def get_count(self):
        if self._type == "INF":
            return -1
        else:
            self._mgr.get_value()
