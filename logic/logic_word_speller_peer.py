#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import time, random
from obci_utils import tags_helper
from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from logic import logic_helper
from gui.ugm import ugm_helper
from logic.engines.speller_engine import SpellerEngine

from obci_configs import settings, variables_pb2
from logic import logic_logging as logger
LOGGER = logger.get_logger("logic_speller", "info")

class LogicWordSpeller(ConfiguredMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses, type=peers.LOGIC_DECISION):
        super(LogicWordSpeller, self).__init__(addresses=addresses,
                                            type=type)
        self._message = ""
        self._last_dec_time = 0

        words = self.config.get_param('words').split(';')
        random.shuffle(words)
        self.words = words
        self.bye_msg = self.config.get_param('bye_msg')
        self.bravo_message = self.config.get_param('bravo_msg')
        self.text_id = int(self.config.get_param("ugm_text_id"))
        self.text_ids = [int(i) for i in self.config.get_param("ugm_text_ids").split(';')]
        self.hold_after_dec = float(self.config.get_param('hold_after_dec'))

        assert(len(self.words) > 0)
        self._update_curr()
        self.ready()
        self._update_letters()

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
        LOGGER.info("UPDATE: "+l_str_config)
        ugm_helper.send_config(self.conn, l_str_config, 1)
        
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


    def _update_curr(self):
        try:
            self._curr_word = self.words.pop()
            curr_word = list(self._curr_word)+[' ']*(7-len(self._curr_word))
            random.shuffle(curr_word)
            curr_word = ''.join(curr_word)
            self._curr_letters_clear()
            self._del_ind = random.randint(0, 7)
            self._curr_letters[self._del_ind] = "Cofnij..."
            j = 0
            for i in range(8):
                if i != self._del_ind:
                    self._curr_letters[i] = curr_word[j]
                    j += 1
            self._message = self._get_base_word()

        except IndexError:
            self._message = self.bye_msg
            self._curr_letters_clear()

    def _curr_letters_clear(self):
        self._curr_letters = [""]*8

    def _get_base_word(self):
        return self._curr_word + " | "

    def _get_final_word(self):
        return self._get_base_word() + self._curr_word

if __name__ == "__main__":
    LogicWordSpeller(settings.MULTIPLEXER_ADDRESSES).loop()

