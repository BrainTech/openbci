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

class DrawBlock2(object):
    BLOCK_TYPE = {'left':[(290, 265), (290, 215), (90, 215), (90, 265)],
             'right':[(350, 265), (350, 215), (550, 215), (550, 265)],
             'up':[(295, 210), (345, 210), (345, 10), (295, 10)],
             'down':[(295, 270), (345, 270), (345, 470), (295, 470)]}

    COLORS = {'black'  : (  0,   0,   0),
              'white'  : (255, 255, 255),
              'yellow' : (255, 213,   0),
              'green'  : ( 68, 253,  68),
              'red'    : (255,   0,   0),
              'gray'   : ( 57,  57,  63),
              'blue'   : (146, 228, 253),
              'green_2'  : ( 0, 100,  0)}

    def __init__(self, window, block_type, color='white'):
        super(DrawBlock2, self).__init__()
        self.window = window
        self.block_type = block_type
        self.points = self.BLOCK_TYPE[block_type]
        pygame.draw.polygon(self.window, self.COLORS[color], self.points)

    def draw_white_block(self):
        pygame.draw.polygon(self.window, self.COLORS['white'], self.BLOCK_TYPE[self.block_type])

    
    def draw_level(self, level):
        if self.block_type == 'left':
            points_level = [[self.points[1][0]-level, self.points[1][1]],
                            [self.points[0][0]-level, self.points[0][1]]]

        elif self.block_type =='right':
            points_level = [[self.points[1][0]+level, self.points[1][1]],
                            [self.points[0][0]+level, self.points[0][1]]]

        elif self.block_type =='up':
            points_level = [[self.points[1][0], self.points[1][1]-level],
                           [self.points[0][0], self.points[0][1]-level]]
                           
        else:
            points_level = [[self.points[1][0], self.points[1][1]+level],
                            [self.points[0][0], self.points[0][1]+level]]

        if level != 0:
            pygame.draw.line(self.window, self.COLORS['gray'], points_level[0], points_level[1], 5)
            pygame.draw.line(self.window, self.COLORS['green_2'], points_level[0], points_level[1], 3)


