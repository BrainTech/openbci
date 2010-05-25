# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#      Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client
import variables_pb2

from data_storage import signal_saver_control
from data_storage import csv_manager
from ugm.ugm_config_manager import UgmConfigManager
from experiment_builder import keystroke
import time
import settings
import os.path
import random
from openbci.tags import tagger
TAGGER = tagger.get_tagger()

INIT_SLEEP = 5
WORD_FILE = 'word'
LONG_FILE = 'long'
SLEEP_FIX_MIN = 0.5
SLEEP_FIX_MAX = 1.5
SLEEP_MASK = 0.05
SLEEP_WORD = 0.028
SLEEP_LONG = 5

class DataManager(object):
    def __init__(self):
        self.images = self.get_images()
        self.words = self.get_words()
    def get_images(self):
        l_files = []
        l_dir = os.path.join(settings.module_abs_path(), 'images')
        for i_file in os.listdir(l_dir):
            if i_file.endswith('bmp'):
                 l_files.append(os.path.join(l_dir, i_file))
        return l_files
    def get_words(self):
        l_groups = []
        l_csv_file = os.path.join(settings.module_abs_path(), 'words')
        l_csv_file = os.path.join(l_csv_file, 'words.csv')
        l_csv_reader = csv_manager.Reader(l_csv_file)
        for i_row in l_csv_reader:
            print(i_row)
            if len(i_row[0]) == 0:
                #end of group
                l_groups.append(l_group)
            elif i_row[0] == 'grupa':
                #new group
                l_group = []
            else:
                l_group.append(i_row)
        l_csv_reader.close()
        random.shuffle(l_groups)
        
        l_words = []
        for i_group in l_groups:
            l_words = l_words + i_group
        return l_words
        
    def next_image(self):
        return random.choice(self.images)

    def words_count(self):
        return len(self.words) # sgdsgds

class Experiment(object):
    def __init__(self):
        self._connection = connect_client(type = peers.LOGIC)
        self._long_mgr = UgmConfigManager()
        self._long_mgr.update_from_file(LONG_FILE, True)
        self._word_mgr = UgmConfigManager()
        self._word_mgr.update_from_file(WORD_FILE, True) 

        self.fixation = '+'
        self.mask = 'XXXXXXXXXXXXXX'
        self.available_keys = ['1','2','3','4','5']
        self.word_config = {'id':5555, 'message':''}
        self.img_config = {'id':6666, 'image_path':''}
        self.data_manager = DataManager()
        self.run_tag = {}
    def run(self):
        #time.sleep(INIT_SLEEP)
        l_saver_control = signal_saver_control.SignalSaverControl()
        l_saver_control.start_saving()
        self.send_text(u"Gotowy? Aby rozpocząć wciśnij '1'.")
        keystroke.wait(['1'])
        for i in range(self.data_manager.words_count()):
            self.send_fixation()
            self.send_mask1()
            self.send_word(self.data_manager.words[i])
            self.send_mask2()
            self.send_long_view()
            self.send_run_tag()
        self.send_text(u"Dziękujemy")
        print("ALL DONE", l_saver_control.finish_saving())

    def send_text(self, text):
        self.word_config['message'] = text
        self._word_mgr.set_config(self.word_config)
        self.send_to_ugm(self._word_mgr.config_to_message(), 0)

    def send_fixation(self):
        self.word_config['message'] = self.fixation
        self._word_mgr.set_config(self.word_config)
        self.send_to_ugm(self._word_mgr.config_to_message(), 0)

        self.run_tag['fix_start_timestamp'] = time.time()
        time.sleep(SLEEP_FIX_MIN + random.random()*(SLEEP_FIX_MAX-SLEEP_FIX_MIN))
        pass
    def send_mask1(self):
        self.send_mask('mask1_start_timestamp')
    def send_mask2(self):
        self.send_mask('mask2_start_timestamp')
    def send_mask(self, tag_entry):
        self.word_config['message'] = self.mask
        self.send_to_ugm(str([self.word_config]))

        self.run_tag[tag_entry] = time.time()
        time.sleep(SLEEP_MASK)
        pass
    def send_word(self, word):
        self.word_config['message'] = word[1]
        self.send_to_ugm(str([self.word_config]))

        self.run_tag['word_start_timestamp'] = time.time()
        self.run_tag['word_message'] = word[1]
        self.run_tag['word_group'] = word[0]
        time.sleep(SLEEP_WORD)

    def send_long_view(self):
        self.img_config['image_path'] = self.data_manager.next_image()
        self._long_mgr.set_config(self.img_config)
        self.send_to_ugm(self._long_mgr.config_to_message(), 0)
        start = time.time()
        # Now wait for user input
        key = keystroke.wait(self.available_keys)
        end = time.time()
        self.run_tag['key_start_timestamp'] = start
        self.run_tag['key_end_timestamp'] = end
        self.run_tag['key_answer'] = key
        #time.sleep(SLEEP_LONG)
    def send_run_tag(self):
        now = time.time()
        TAGGER.send_tag(now, now, 'experiment_run', self.run_tag)

    def send_to_ugm(self, config_value, msg_type=1):
        l_type = msg_type
        l_msg = variables_pb2.UgmUpdate()
        l_msg.type = int(l_type)
        l_msg.value = config_value
        self._connection.send_message(
            message = l_msg.SerializeToString(), 
            type=types.UGM_UPDATE_MESSAGE, flush=True)
        
if __name__ == "__main__":
    Experiment().run()
