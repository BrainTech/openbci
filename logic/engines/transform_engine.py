#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
#import os.path, sys, time, os
import time
from obci.logic import logic_helper
from obci.gui.ugm import ugm_helper
from obci.devices import diode_helper
from obci.utils import context as ctx

class TransformEngine(object):
    def __init__(self, configs, context=ctx.get_dummy_context('TransformEngine')):
        self.logger = context['logger']
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
            self.logger.info("Restart scenario!!!")
            ugm_helper.send_hide(self.conn)
            logic_helper.restart_scenario(self.conn, self._configs[to_interface],
                                          leave_on=['amplifier'])
