#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import time
from obci_utils import tags_helper
from multiplexer.multiplexer_constants import peers, types
from logic import logic_helper
from logic.logic_decision_peer import LogicDecision
from logic.engines.speller_engine import SpellerEngine
from logic.engines.transform_engine import TransformEngine
from obci_utils import context as ctx
from obci_configs import settings, variables_pb2

class LogicTransform(LogicDecision, SpellerEngine, TransformEngine):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        context = ctx.get_new_context()
        context['logger'] = self.logger
        LogicDecision.__init__(self, addresses=addresses, context)
        SpellerEngine.__init__(self, self.config.param_values(), context)
        TransformEngine.__init__(self, self.config.param_values(), context)
        self.ready()
        self._update_letters()

    def _run_post_actions(self, p_decision):
        self._update_letters()

if __name__ == "__main__":
    LogicTransform(settings.MULTIPLEXER_ADDRESSES).loop()

