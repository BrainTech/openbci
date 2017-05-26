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

import os.path
from obci.configs import settings

import pygame
pygame.mixer.init()
from pygame.locals import *
from draw_block import DrawBlock
from obci.exps.ventures.maze_game.screen_text.render_textrect import *
from screen_text import *

GAME_DATA_PATH = os.path.join(settings.MAIN_DIR, 'exps/ventures/maze_game/game_data')

class CalibrationScreen(object): 
    SCREEN_SIZE = (640, 480) 
    
    def __init__(self):
        super(CalibrationScreen, self).__init__()
        pygame.init()
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE, FULLSCREEN)
        pygame.display.init()
        self._init_blocks()
        self._init_level_max()
        self.set_calibration_last_value(0,0,0,0)
        self._load_resources()
        self.text_rect = pygame.Rect((0, 10, 640, 470))

    def _load_resources(self):
        self.font_text = pygame.font.Font(os.path.join(GAME_DATA_PATH,'impact.ttf'), 24)
        self.black_screen = pygame.image.load(os.path.join(GAME_DATA_PATH,'blank.gif'))

    def _value2px(self, value):
        return int(self.get_block_size()*(float(value)/100))

    def set_calibration_last_value(self, up, right, down, left):
        self.get_block('up').set_level_last(self._value2px(up))
        self.get_block('right').set_level_last(self._value2px(right))
        self.get_block('down').set_level_last(self._value2px(down))
        self.get_block('left').set_level_last(self._value2px(left))

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

    def _init_level_max(self):
        self.level_max_left = 0
        self.level_max_right = 0
        self.level_max_up = 0
        self.level_max_down = 0

    def _init_blocks(self):
        self.block_right = DrawBlock(self.screen, 'right')
        self.block_left = DrawBlock(self.screen, 'left')
        self.block_up = DrawBlock(self.screen, 'up')
        self.block_down = DrawBlock(self.screen, 'down')

    def _display(self): 
        pygame.display.flip()

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

    def update_level_max(self, level_max_type, value):
        if level_max_type == 'right' and value > self.level_max_right:
            self.level_max_right=value

        elif level_max_type == 'left' and value > self.level_max_left:
            self.level_max_left = value

        elif level_max_type == 'up' and value > self.level_max_up:
            self.level_max_up = value

        elif level_max_type == 'down' and value > self.level_max_down:
            self.level_max_down = value

    def get_level_max(self, level_max_type):
        if level_max_type == 'right':
            return self.level_max_right

        elif level_max_type == 'left':
            return self.level_max_left

        elif level_max_type == 'up':
            return self.level_max_up

        elif level_max_type == 'down':
            return self.level_max_down

    def get_block_size(self):
        return 200

    def update_block(self, block_type, level):
        if block_type != 'baseline':
            level = self._value2px(level)
            self.update_level_max(block_type, level)
            self.get_block(block_type).draw_level(level, self.get_level_max(block_type))
        for block_t in ['right', 'left', 'down', 'up']:
            if not block_t == block_type:
                self.get_block(block_t).draw_level(0, self.get_level_max(block_t))
        self._display()
