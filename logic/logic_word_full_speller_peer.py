#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import time, random
from obci.logic.logic_decision_peer import LogicDecision
from obci.logic.engines.speller_engine import SpellerEngine
from obci.logic.engines.word_speller_engine import WordSpellerEngine
from obci.utils import context as ctx
from obci.configs import settings
from obci.utils.openbci_logging import log_crash
from multiplexer.multiplexer_constants import peers, types

class LogicSpeller(LogicDecision, SpellerEngine, WordSpellerEngine):
    @log_crash
    def __init__(self, addresses):
        LogicDecision.__init__(self, addresses=addresses)
        context = ctx.get_new_context()
        context['logger'] = self.logger
        SpellerEngine.__init__(self, self.config.param_values(), context)
        WordSpellerEngine.__init__(self, self.config.param_values())
        
        self.update_curr_dec = int(self.config.get_param('update_curr_dec'))

        self.bravo_message = self.config.get_param('bravo_msg')

        self._update_curr()
        self.ready()
        self._update_letters()

    @log_crash
    def handle_message(self, mxmsg):
        if (mxmsg.type == types.DECISION_MESSAGE):
            dec = int(mxmsg.message)
            if dec == self.update_curr_dec:
                if not self._update_curr():
                    self._state_machine.set_next_state(9)
                else:
                    self._state_machine.set_next_state(8)                    
                self._update_letters()
                self.no_response()
            else:
                LogicDecision.handle_message(self, mxmsg)
    @log_crash
    def _run_post_actions(self, p_decision):
        if self._message == self._get_final_word():
            self._state_machine.set_next_state(8)
            self._update_letters()
            time.sleep(2)
            self._message = self.bravo_message
        self._update_letters()

if __name__ == "__main__":
    LogicSpeller(settings.MULTIPLEXER_ADDRESSES).loop()

