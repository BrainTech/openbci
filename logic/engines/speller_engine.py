#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import os.path, sys, time, os
from gui.ugm import ugm_helper
from logic import logic_logging as logger
LOGGER = logger.get_logger("speller_engine", "info")


class SpellerEngine(object):
    def __init__(self, configs):
        self._message = ""
        self.text_id = int(configs["ugm_text_id"])
        self.text_ids = [int(i) for i in configs["ugm_text_ids"].split(';')]

    # --------------------------------------------------------------------------
    # ------------------ actions available in config ---------------------------
    def backspace(self):
        """Run backspace action -> truncate self._message.
        A place where this action is defined to be fired
        is speller config file.
        """
        self._message = self._message[:len(self._message) - 1]

    def say(self, msg=None):
        """Run say action -> run external program with self._message
        as a paramtere.
        A place where this action is defined to be fired
        is speller config file.
        """
        if not msg:
            msg = self._message
        LOGGER.info("TRYING TO SAY: "+msg)
        self.run_ext(u''.join(
                [#u'milena_say ', msg, u" &"
                    u'echo "', msg,'" | ',
                    "festival --tts",
                    " &"
                 ]))

    def msg(self, p_message):
        """Update stored message."""
        self._message = u''.join([self._message, p_message])

    def clear(self):
        """Update stored message as empty
        """
        self._message = u''

    def close_dasher(self):
        self._message = os.popen('xsel -b').read().decode('utf-8')
        os.system('killall dasher')


    def _update_letters(self):
        """Sent to self._server current logic data:
        - current message,
        """
        LOGGER.info("UPDATE MESSAGE: "+self._message)
        l_config = []

        l_letters = self._compute_current_letters()
        for i, i_letters in enumerate(l_letters):
            l_conf = {'id':self.text_ids[i],
                      'message':i_letters}
            l_config.append(l_conf)
        l_config.append({'id':self.text_id,
                         'message':self._message})
        l_str_config = str(l_config)
        LOGGER.info("UPDATE: "+l_str_config)
        ugm_helper.send_config(self.conn, l_str_config, 1)
            

    def _compute_current_letters(self):    
        """Return collection of strings representing current`s state graphics. 
        See _compute_current_param for details.
        """
        return self._compute_current_param('letters', 'letters_solver')

        
