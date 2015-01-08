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
from draw_block import DrawBlock

class CalibrationScreen(object): 
    SCREEN_SIZE = (640, 480) 
    
    def __init__(self):
        super(CalibrationScreen, self).__init__()
        pygame.init()
        self.screen = pygame.display.set_mode(self.SCREEN_SIZE)#, FULLSCREEN)
        pygame.display.init()
        self._init_blocks()
        self._display()

    def _init_blocks(self):
        self.block_right = DrawBlock(self.screen, 'right')
        self.block_left = DrawBlock(self.screen, 'left')
        self.block_up = DrawBlock(self.screen, 'up')
        self.block_down = DrawBlock(self.screen, 'down')

    def _display(self):
        pygame.display.flip()

    def get_block(self, block_type):
        if block_type == 'right':
            return self.block_right

        elif block_type == 'left':
            return self.block_left

        elif block_type == 'up':
            return self.block_up

        elif block_type == 'down':
            return self.block_down

    def update_block(self, block_type, level):
        self.get_block(block_type).draw_level(level)
        self._display()