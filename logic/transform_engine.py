#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
#import os.path, sys, time, os
from logic import logic_logging as logger
from logic import logic_helper
LOGGER = logger.get_logger("transform_engine", "info")


class TransformEngine(object):
    def __init__(self, configs, current_interface):
        self._current_interface = current_interface
        self._scens = {
            'switch': configs['switch'],
            'ssvep': configs['ssvep']
            }

    def transform_scenario(self, to_interface):
        if self._current_interface == to_interface:
            return
        else:
            logic_helper.restart_scenario(self.conn, self._scens[to_interface],
                                          leave_on=['amplifier'])
