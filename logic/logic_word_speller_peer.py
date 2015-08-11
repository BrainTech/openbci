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

        self._last_dec_time = 0
        self.hold_after_dec = float(self.config.get_param('hold_after_dec'))

        self.bravo_message = self.config.get_param('bravo_msg')

        self._update_curr()
        self.ready()
        self._update_letters()
    @log_crash
    def handle_message(self, mxmsg):
        if self._last_dec_time > 0:
            t = time.time() - self._last_dec_time
            if t > self.hold_after_dec:
                self._last_dec_time = 0
                self._update_curr()
                self._update_letters()
            self.no_response()
        elif (mxmsg.type == types.DECISION_MESSAGE):
            dec = int(mxmsg.message)
            if dec == self._del_ind:
                if self._message == self._get_base_word():
                    pass
                else: 
                    self._message = self._message[:len(self._message) - 1]
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
            self._last_dec_time = time.time()
            self._curr_letters_clear()
            self._update_letters()
            time.sleep(2)
            self._message = self.bravo_message
            self._update_letters()
        else:
            self._update_letters()



if __name__ == "__main__":
    LogicWordSpeller(settings.MULTIPLEXER_ADDRESSES).loop()

