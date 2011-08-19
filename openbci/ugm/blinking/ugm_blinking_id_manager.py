#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sequence_provider
class DummyProvider(object):
    def get_value(self):
        return 0

class UgmBlinkingIdManager(object):
    def get_requested_configs(self):
        return ['BLINK_ID_TYPE', 'BLINK_ID_COUNT']

    def set_configs(self, configs):
        self._type = configs['BLINK_ID_TYPE']
        self._blink_count = int(configs['BLINK_ID_COUNT'])
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



