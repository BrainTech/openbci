#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

from multiplexer.multiplexer_constants import peers, types
from obci.logic import logic_helper
from obci.logic.logic_decision_peer import LogicDecision
from obci.logic.engines.speller_engine import SpellerEngine
from obci.logic.engines.robot_engine import RobotEngine
from obci.logic.engines.maze_engine import MazeEngine
from obci.utils import context as ctx
from obci.gui.ugm import ugm_helper
from obci.configs import settings, variables_pb2

import time

class LogicMaze(LogicDecision, SpellerEngine, RobotEngine, MazeEngine):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        LogicDecision.__init__(self, addresses=addresses)
        context = ctx.get_new_context()
        context['logger'] = self.logger
        SpellerEngine.__init__(self, self.config.param_values(), context)
        RobotEngine.__init__(self, self.config.param_values(), context)
        self._maze_finished = False
        self._maze_success = False
        MazeEngine.__init__(self, self.config.param_values(), context)
        self.ready()
        time.sleep(2)
        self._update_letters()

    def _run_post_actions(self, p_decision):
        self._update_letters()
        if not self._maze_finished and self._maze_success:
            self._maze_finished = True
            time.sleep(5)
            #to restart scenario ... assumed switch_backup module is on - quite lame, but effective by now ...
            self.conn.send_message(message = "",
                                   type = types.SWITCH_MESSAGE, flush=True)
            
if __name__ == "__main__":
    LogicMaze(settings.MULTIPLEXER_ADDRESSES).loop()

