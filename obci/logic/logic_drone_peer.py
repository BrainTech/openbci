#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import os.path, sys, time, os
#import speller_graphics_manager as sgm

from multiplexer.multiplexer_constants import peers, types
from obci.configs import settings, variables_pb2
from obci.utils import context as ctx
from obci.logic.logic_speller_peer import LogicSpeller
from obci.logic.engines.robot_drone_engine import RobotEngine

class LogicRobot(LogicSpeller, RobotEngine):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        LogicSpeller.__init__(self, addresses=addresses)
        context = ctx.get_new_context()
        context['logger'] = self.logger
        RobotEngine.__init__(self,  self.config.param_values(), context)
        self.ready()
        self._update_letters()

    def _run_post_actions(self, p_decision):
        self._update_letters()

if __name__ == "__main__":
    LogicRobot(settings.MULTIPLEXER_ADDRESSES).loop()
