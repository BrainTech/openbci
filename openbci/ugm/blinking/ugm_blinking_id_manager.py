#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import sequence_provider
class DummyProvider(object):
    def get_value(self):
        return 0

class UgmBlinkingIdManager(object):
    """Provides ids of subsequent blinks. Eg for speller with 4 cols and 2 rows it should reutrn values in [0...5]"""
    def get_requested_configs(self):
        return ['BLINK_ID_TYPE', # An algorithm generationg ids. Possible values:
                    # RANDOM - random values from range [0;BLINK_ID_COUNT]
                    # SEQUENTIAL - sequental values from range [0;BLINK_ID_COUNT]
                    # RANDOM_SEQUENTIAL - random, but not repeated values from 0 to BLINK_ID_COUNT. Eg. for [0,1,2,3] we`ll get
                    # sth like 0 2 3 1  2 3 0 1  3 1 0 2  0 2 1 3 .... 
                'BLINK_ID_COUNT'# ids will be genereated from range [0;BLINK_ID_COUNT]
                ]

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



