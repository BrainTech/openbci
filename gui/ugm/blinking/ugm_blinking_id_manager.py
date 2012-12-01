#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

from obci.utils import sequence_provider
class DummyProvider(object):
    def get_value(self):
        return 0

class UgmBlinkingIdManager(object):
    """Provides ids of subsequent blinks. Eg for speller with 4 cols and 2 rows it should reutrn values in [0...5]"""

    def set_configs(self, configs):
        self._type = configs.get_param('blink_id_type')
        self._blink_count = int(configs.get_param('blink_id_count'))
        assert(self._blink_count >= 0)
        self.reset()

    def reset(self):
        if self._blink_count > 0:
            self._mgr = sequence_provider.PROVIDERS[self._type](
                0,
                self._blink_count
                )
        else:
            self._mgr = DummyProvider()

    def get_id(self):
        return self._mgr.get_value()



