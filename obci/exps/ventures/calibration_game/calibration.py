# -*- coding: utf-8 -*-
#!/usr/bin/env python
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
#     Anna Chabuda <anna.chabuda@gmail.com>
#

import pygame
from pygame.locals import *
pygame.mixer.init()

from obci.exps.ventures.calibration_game.calibration_screen import CalibrationScreen
from obci.exps.ventures import logic_queue
from obci.exps.ventures.data.data_manager import calibration_get_last
from obci.exps.ventures.maze_game.tags.tagger import Tagger
import time

class Calibration(logic_queue.LogicQueue):
    def __init__(self, user_id, tag_name, tag_dir):
        super(Calibration, self).__init__()
        self.screen = CalibrationScreen()
        self.user_id = user_id
        self._init_calibration_last_data()
        self.tagger_init(tag_name, tag_dir)

    def _init_calibration_last_data(self):
            data  = calibration_get_last(self.user_id)
            if data != None:
                up, right, down, left, t  = data
                self.screen.set_calibration_last_value(100*float(up), 100*float(right), 100*float(down), 100*float(left))

    def tagger_init(self, tag_name, tag_dir):
        self.tagger = Tagger(tag_name, tag_dir, status='ON')

    def send_tag(self, timestamp, tag_name, tage_value=''):
        self.tagger.set_tag(timestamp, str(tag_name), str(tage_value))

    def save_tags(self):
        self.tagger.finish()

    def instruction(self):
        screens = ['start', 'instruction']
        screen_status = 0
        self.screen.display_screen(screens[screen_status])
        while screen_status<len(screens):
            for event in pygame.event.get():                    
                if event.type == KEYDOWN:            
                    if event.key == K_SPACE:
                        screen_status+=1 
                        if screen_status<len(screens):
                            self.screen.display_screen(screens[screen_status])

    def run(self):
        self.instruction()
        self.screen.display_calib_start()
        done = False
        self.clear_queue() 
        while not done:
            for event in pygame.event.get():                  
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self._finish_calibration()
                    done = True
            sample = self.get_message()
            if sample is not None:  
                self.screen.update_block(sample.key, sample.value)

    def _finish_calibration(self):
        right, left, up, down = self.screen.get_level_max_()
        self.send_tag(time.time(), 'right', float(right)/100)
        self.send_tag(time.time(), 'left', float(left)/100)
        self.send_tag(time.time(), 'up', float(up)/100)
        self.send_tag(time.time(), 'down', float(down)/100)
        self.save_tags()


        
