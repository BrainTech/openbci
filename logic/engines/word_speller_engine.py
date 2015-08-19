#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#    

import random

class WordSpellerEngine(object):
    def __init__(self, configs):
        self._message = ""
        words = configs['words'].split(';')
        random.shuffle(words)
        self.words = words
        self.scatter_randomly = int(configs['scatter_randomly'])
        assert(len(self.words) > 0)
        self.bye_msg = configs['bye_msg']

    def _update_curr(self):
        try:
            self._curr_word = self.words.pop()
            curr_word = list(self._curr_word)+[' ']*(7-len(self._curr_word))
            if self.scatter_randomly:
                random.shuffle(curr_word)
                self._del_ind = random.randint(0, 7)
            else:
                self._del_ind = 7                

            curr_word = ''.join(curr_word)
            self._curr_letters_clear()
            self._curr_letters[self._del_ind] = "SKASUJ"
            j = 0
            for i in range(8):
                if i != self._del_ind:
                    self._curr_letters[i] = curr_word[j]
                    j += 1
            self._message = self._get_base_word()
            return 0

        except IndexError:
            self._message = self.bye_msg
            self._curr_letters_clear()
            return 1

    def _curr_letters_clear(self):
        self._curr_letters = [""]*8

    def _get_base_word(self):
        return self._curr_word + " | "

    def _get_final_word(self):
        return self._get_base_word() + self._curr_word

    def word_backspace(self):
        if self._message not in [self._get_base_word(), self.bye_msg, self.bravo_message]:
            self._message = self._message[:len(self._message) - 1]            
            
