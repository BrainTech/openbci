#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import time, random
from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.gui.ugm import ugm_helper
from obci.logic.engines.speller_engine import SpellerEngine
from obci.logic.engines.word_speller_engine import WordSpellerEngine
from obci.configs import settings
from obci.utils.openbci_logging import log_crash

class LogicWordSpeller(ConfiguredMultiplexerServer, WordSpellerEngine):
    @log_crash
    def __init__(self, addresses, type=peers.LOGIC_DECISION):
        ConfiguredMultiplexerServer.__init__(self, 
                                             addresses=addresses,
                                             type=type)
        WordSpellerEngine.__init__(self, self.config.param_values())

        self.text_id = int(self.config.get_param("ugm_text_id"))
        self.text_ids = [int(i) for i in self.config.get_param("ugm_text_ids").split(';')]

        self.update_curr_dec = int(self.config.get_param('update_curr_dec'))

        self.bravo_message = self.config.get_param('bravo_msg')

        self._is_break = False

        self._update_curr()
        self.ready()
        self._update_letters()
    @log_crash
    def handle_message(self, mxmsg):
        if (mxmsg.type == types.DECISION_MESSAGE):
            dec = int(mxmsg.message)
            if dec == self.update_curr_dec:
                self._is_break = self._update_curr()#update_curr returns true if there are no word left
                self._update_letters()
            elif not self._is_break:
                if dec == self._del_ind:
                    self.word_backspace()
                    self._update_letters()
                else:
                    self.msg(dec)

        self.no_response()

    def _update_letters(self):
        l_config = []
        l_letters = self._curr_letters
        for i, i_letters in enumerate(l_letters):
            l_conf = {'id':self.text_ids[i],
                      'message':i_letters}
            l_config.append(l_conf)
        l_config.append({'id':self.text_id,
                         'message':self._message})
        l_str_config = str(l_config)
        self.logger.info("UPDATE: "+l_str_config)
        ugm_helper.send_config(self.conn, l_str_config, 1)
    @log_crash        
    def msg(self, dec):
        self._message = ''.join([self._message, self._curr_letters[dec]])
        if self._message == self._get_final_word():
            self._is_break = True
            self._curr_letters_clear()
            self._update_letters()
            time.sleep(2)
            self._message = self.bravo_message
        self._update_letters()



if __name__ == "__main__":
    LogicWordSpeller(settings.MULTIPLEXER_ADDRESSES).loop()

