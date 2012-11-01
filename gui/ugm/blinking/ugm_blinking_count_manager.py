#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

from obci_utils import sequence_provider
class DummyProvider(object):
    def get_value(self):
        return -1

class UgmBlinkingCountManager(object):
    """For how long should blinker blink? This class provides rules for that. 
    It returns an int indicating number of blinks to 'stop blinking'.
    Blinking is stopped until blinker receives message 'start_blinking'"""

    def set_configs(self, configs):
        self._type = configs.get_param('blink_count_type')
        self._start = int(configs.get_param('blink_count_min'))
        self._count = int(configs.get_param('blink_count_max')) - self._start
        assert(self._start >= 0)
        assert(self._count >= 0)
        self.reset()

    def reset(self):
        if self._type != "inf":
            self._mgr = sequence_provider.PROVIDERS[self._type](
                self._start,
                self._count
                )
        else:
            self._mgr = DummyProvider()

    def get_count(self):
        return self._mgr.get_value()
