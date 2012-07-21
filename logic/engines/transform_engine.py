#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
#import os.path, sys, time, os
from logic import logic_logging as logger
from logic import logic_helper
from devices import diode_helper
LOGGER = logger.get_logger("transform_engine", "info")


class TransformEngine(object):
    def __init__(self, configs):
        self._configs = configs
        self._current_interface = configs['default_mode']
        self._is_transforming = False

    def transform_scenario(self, to_interface):
        if self._current_interface == to_interface:
            return
        elif not self._is_transforming:#can fire only once...
            self._is_transforming = True
            if self._current_interface.startswith('ssvep'):
                diode_helper.diode_stop(self.conn)

            self._current_interface = to_interface
            logic_helper.restart_scenario(self.conn, self._configs[to_interface],
                                          leave_on=['amplifier'])
