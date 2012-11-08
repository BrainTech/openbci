#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
#import os.path, sys, time, os
import time
from logic import logic_logging as logger
from logic import logic_helper
from gui.ugm import ugm_helper
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
            self._current_interface = to_interface
            time.sleep(0.3)# wait a moment, maybe gui wants to take a while before hiding
            #restarting takes many seconds anyway...
            ugm_helper.send_hide(self.conn)
            logic_helper.restart_scenario(self.conn, self._configs[to_interface],
                                          leave_on=['amplifier'])
