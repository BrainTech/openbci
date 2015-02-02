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
pygame.mixer.init()
import time

from pygame.locals import *

from maze_logic import MazeLogic

from maze_wii_level import MazeWiiLevel
from arrow.wii_arrow import WiiArrow

from constants.constants_game import FRAME_RATE

class Sample(object):
    """docstring for Sample"""
    def __init__(self, direction):
        super(Sample, self).__init__()
        self.value = 0
        self.key = direction

def get_sample():
        return Sample('down')


class MazeWiiLogic(MazeLogic):
    def __init__(self, start_level, start_wii_data, session_number, session_duration, 
                 time_board_display, time_left_out, tagger, session_type, session_condition,
                 data_engine):
        super(MazeWiiLogic, self).__init__(start_level, session_number, session_duration, 
                                           time_board_display, time_left_out, 
                                           tagger, session_type, session_condition)
        self.data_engine = data_engine
        self.start_wii_level = 1
        self.wii_level = MazeWiiLevel(session_type, self.init_wii_level(start_wii_data))
        self._init_wii_arrows()

    def init_wii_level(self, start_wii_data):
        return {'right':{'step_up':1, 'step_down':1, 'area_start_value':int(start_wii_data['right'])-40,'area_end_value':int(start_wii_data['right'])},
                'left':{'step_up':1, 'step_down':1, 'area_start_value':int(start_wii_data['left'])-40,'area_end_value':int(start_wii_data['left'])},
                'down':{'step_up':1, 'step_down':1, 'area_start_value':int(start_wii_data['down'])-40,'area_end_value':int(start_wii_data['down'])},
                'up':{'step_up':1, 'step_down':1, 'area_start_value':int(start_wii_data['up'])-40,'area_end_value':int(start_wii_data['up'])}}

    def _init_wii_arrows(self):
        self.wii_arrows = {'right' : WiiArrow('right'),
                           'left':  WiiArrow('left'),
                           'down' : WiiArrow('down'),
                           'up' : WiiArrow('up')}

    def set_current_wii_level(self, level):
        self.current_wii_level = {'right' : level,
                                  'left':  level,
                                  'down' : level,
                                  'up' : level}

    def get_current_wii_level(self, direction):
        return self.current_wii_level[direction]

    def get_current_wii_levels(self, direction):
        return self.current_wii_level['up'], self.current_wii_level['down'], self.current_wii_level['left'], self.current_wii_level['right']

    def update_current_wii_level(self, direction):
        self.current_wii_level[direction] += 1
        print self.current_wii_level


    def set_current_arrow_direction(self, direction):
        self.current_arrow_direction = direction

    def get_current_arrow_direction(self):
        return self.current_arrow_direction

    def get_current_arrow(self):
        if self.current_arrow_direction != None:
            return self.wii_arrows[self.current_arrow_direction]
        else:
            return None

    def is_move(self):
        if self.current_arrow_direction != None:
            return self.wii_arrows[self.current_arrow_direction].is_move()
        else:
            return False

    def load_wii_level(self, direction):
        for arrow in self.wii_arrows.values():
            if arrow.direction==direction:
                self.wii_level.load_level(arrow.direction, self.get_current_wii_level(direction))
                level_params = self.wii_level.get_level(arrow.direction)
                arrow.set_level(*level_params)
                self.screen.load_wii_level_arrow_proportion(arrow.direction, level_params[2:])

    def draw_game_with_arrow(self, arrow_type):
        self.screen.draw_game_with_wii_arrow(arrow_type,
                                             self.get_current_arrow().get_arrow_level(),
                                             self.get_current_arrow().get_area_state(),
                                             self.get_level_array(),
                                             self.get_ball_position_x(),
                                             self.get_ball_position_y(),
                                             self.get_current_level(),
                                             self.get_level_time(),
                                             self.get_session_time(),
                                             self.get_path(),
                                             self.get_active_path())

    def draw_game_with_arrow_update(self, arrow_type):
        self.screen.draw_game_with_wii_arrow_update(arrow_type,
                                                    self.get_current_arrow().get_arrow_level(),
                                                    self.get_current_arrow().get_area_state(),
                                                    self.get_level_array(),
                                                    self.get_ball_position_x(),
                                                    self.get_ball_position_y(),
                                                    self.get_current_level(),
                                                    self.get_level_time(),
                                                    self.get_session_time(),
                                                    self.get_path(),
                                                    self.get_active_path())
        

    def update_screen(self):
        sample = self.data_engine.get_message()
        #sample = get_sample()
        if sample is not None:
            if sample.key == self.get_current_arrow_direction():
                self.get_current_arrow().update(sample.value)
                self.draw_game_with_arrow(sample.key)
            elif sample.key == 'baseline':
                if self.get_current_arrow_direction() != None:
                    self.get_current_arrow().reset()
                self.draw_game()
            else:
                if self.get_current_arrow_direction() != None:
                    self.get_current_arrow().reset()
                    self.set_current_arrow_direction(sample.key)
                    self.get_current_arrow().update(sample.value)
                    self.draw_game_with_arrow(sample.key)
                else:
                    self.set_current_arrow_direction(sample.key)
                    self.get_current_arrow().update(sample.value)
                    self.draw_game_with_arrow(sample.key)
            if self.is_move():
                self.send_tag(time.time(), 'move', self.get_current_arrow_direction())
                self.move(self.get_current_arrow_direction())
                self.update_current_wii_level(self.get_current_arrow_direction())
                self.load_wii_level(self.get_current_arrow_direction())
                self.get_current_arrow().reset()
                self.set_current_arrow_direction(None)

        for event in pygame.event.get():
            if event.type == QUIT:
                    self.exit_game()

            elif event.type == KEYDOWN:           
                if event.key == K_ESCAPE:
                    self.exit_game()

                elif event.key == K_p:
                    self.make_pause()

    def level_start(self):
        super(MazeWiiLogic, self).level_start()
        self.data_engine.clear_queue()     

    def move(self, p):
        super(MazeWiiLogic, self).move(p)
        self.data_engine.clear_queue()

    def make_pause(self):
        super(MazeWiiLogic, self).make_pause()
        self.data_engine.clear_queue()

    def exit_game(self):
        super(MazeWiiLogic, self).exit_game()
        self.data_engine.clear_queue()

    def main(self):    
        self.set_current_level(self.start_level)
        self.load_level()  
        self.set_current_wii_level(self.start_wii_level)
        for key in self.current_wii_level.keys():
            self.load_wii_level(key)
        self.set_current_arrow_direction(None)
        self.instruction()
        self.session_start() 
        self.level_start()
        while self.get_current_level()<= self.number_of_levels and self.status:
            if not self.get_level_status():
                self.level_timeout()
            else:
                self.update_screen()
            time.sleep(1/FRAME_RATE)
        self.finish_game()
