#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import time
from obci.utils import tags_helper
from multiplexer.multiplexer_constants import peers, types
from obci.logic import logic_helper
from obci.logic.logic_decision_peer import LogicDecision
from obci.logic.engines.speller_engine import SpellerEngine
from obci.logic.engines.transform_engine import TransformEngine
from obci.utils import context as ctx
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash

class LogicTransform(LogicDecision, SpellerEngine, TransformEngine):
    """A class for creating a manifest file with metadata."""
    @log_crash
    def __init__(self, addresses):
        LogicDecision.__init__(self, addresses=addresses)
        context = ctx.get_new_context()
        context['logger'] = self.logger
        SpellerEngine.__init__(self, self.config.param_values(), context)
        TransformEngine.__init__(self, self.config.param_values(), context)
        self.ready()
        self._update_letters()

    def _run_post_actions(self, p_decision):
        self._update_letters()

if __name__ == "__main__":
    LogicTransform(settings.MULTIPLEXER_ADDRESSES).loop()

