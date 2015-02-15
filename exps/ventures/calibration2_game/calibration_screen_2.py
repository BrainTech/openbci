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
from pygame.locals import *
from draw_block_2 import DrawBlock2 as DrawBlock
from draw_box import DrawBox
from obci.configs import settings
import os.path

from obci.exps.ventures.maze_game.screen_text.render_textrect import *
from screen_text import *

GAME_DATA_PATH = os.path.join(settings.MAIN_DIR, 'exps/ventures/maze_game/game_data')

class CalibrationScreen2(object): 
    SCREEN_SIZE = (640, 480) 
    
    def __init__(self):
        super(CalibrationScreen2, self).__init__()
        pygame.init()
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)#, FULLSCREEN)
        pygame.display.init()
        self._init_blocks()
        self.max_size = 120.0
        self.box = DrawBox(self.screen)
        self._load_resources()
        self.text_rect = pygame.Rect((0, 10, 640, 470))

    def _load_resources(self):
        self.font_text = pygame.font.Font(os.path.join(GAME_DATA_PATH,'impact.ttf'), 24)
        self.black_screen = pygame.image.load(os.path.join(GAME_DATA_PATH,'blank.gif'))
        self.fall_sound = pygame.mixer.Sound(os.path.join(GAME_DATA_PATH,'Fall.wav'))
        self.enter_sound = pygame.mixer.Sound(os.path.join(GAME_DATA_PATH, 'Enter.wav'))

    def _init_blocks(self):
        self.block_right = DrawBlock(self.screen, 'right')
        self.block_left = DrawBlock(self.screen, 'left')
        self.block_up = DrawBlock(self.screen, 'up')
        self.block_down = DrawBlock(self.screen, 'down')

    def _display(self): 
        pygame.display.flip()

    def _display_screen_helper(self, image, text='', color=(250, 250, 250)):
        self.screen.blit(self.black_screen, (0, 0))
        rendered_text = render_textrect(text, self.font_text, self.text_rect, color, (0, 0, 0), 1)
        text = self.font_text.render(text ,1, color)
        self.screen.blit(rendered_text, self.text_rect.topleft)

    def display_screen(self, action):
        if action == 'start':
            self._display_screen_helper(text=get_start_text(), image=self.black_screen)
            self._display()

        elif action == 'instruction':
            self._display_screen_helper(text=get_instruction_text(), image=self.black_screen)
            self._display()
            
    def display_calib_start(self):
        self.screen.blit(self.black_screen, (0, 0))
        self._display()

    def get_block(self, block_type):
        if block_type == 'right':
            return self.block_right

        elif block_type == 'left':
            return self.block_left

        elif block_type == 'up':
            return self.block_up

        elif block_type == 'down':
            return self.block_down

    def get_block_size(self):
        return 200.0

    def display_box(self, direction, level_min, level_max):
        level_min = (self.get_block_size()/self.max_size)*level_min
        level_max = (self.get_block_size()/self.max_size)*level_max
        self.box.init_box(direction, level_min, level_max)

    def clear(self, display=False):
        self.screen.blit(self.black_screen, (0, 0))
        for block_type in ['right', 'left', 'down', 'up']:
            self.get_block(block_type).draw_white_block()
        if display:
            self._display()

    def update_block(self, block_type, level, area_state):
        self.clear()
        self.box.update_box(area_state)
        if block_type != 'baseline':
            level = int((self.get_block_size()/self.max_size)*level)
            self.get_block(block_type).draw_level(level)

        for block_t in ['right', 'left', 'down', 'up']:
            if not block_t==block_type:
                level = 0
                self.get_block(block_t).draw_level(0)
        self._display()

    def update_level(self, block_type, level):
        self.clear()
        if block_type != 'baseline':
            level = int((self.get_block_size()/self.max_size)*level)
            self.get_block(block_type).draw_level(level)

        for block_t in ['right', 'left', 'down', 'up']:
            if not block_t==block_type:
                level = 0
                self.get_block(block_t).draw_level(0)
        # self._display()

    def display_color_box(self, color):
        self.box.draw_box_color(color)
        self._display()

    def play_sound(self, action):
        if action == 'win':
            self.enter_sound.play()

        elif action == 'fall':
            self.fall_sound.play()