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

class DrawBlock(object):
    BLOCK_TYPE = {'left':[(290, 265), (290, 215), (90, 215), (90, 265)],
             'right':[(350, 265), (350, 215), (550, 215), (550, 265)],
             'up':[(295, 210), (345, 210), (345, 10), (295, 10)],
             'down':[(295, 270), (345, 270), (345, 470), (295, 470)]}

    COLORS = {'black'  : (  0,   0,   0),
              'white'  : (255, 255, 255),
              'yellow' : (255, 255,   0),
              'green'  : (  0, 255,   0),
              'red'    : (255,   0,   0),
              'blue'   : (  0,   0, 205)}

    def __init__(self, window, block_type, color='white'):
        super(DrawBlock, self).__init__()
        self.window = window
        self.block_type = block_type
        self.points = self.BLOCK_TYPE[block_type]
        pygame.draw.polygon(self.window, self.COLORS[color], self.points)

    def draw_level(self, level):
        if self.block_type == 'left':
            points = [self.points[0], 
                      self.points[1], 
                      [self.points[1][0]-level, self.points[1][1]],
                      [self.points[0][0]-level, self.points[0][1]]]

        elif self.block_type =='right':
            points = [self.points[0], 
                      self.points[1], 
                      [self.points[1][0]+level, self.points[1][1]],
                      [self.points[0][0]+level, self.points[0][1]]]
        elif self.block_type =='up':
            points = [self.points[0], 
                      self.points[1], 
                      [self.points[1][0], self.points[1][1]-level],
                      [self.points[0][0], self.points[0][1]-level]]
        else:
            points = [self.points[0], 
                      self.points[1], 
                      [self.points[1][0], self.points[1][1]+level],
                      [self.points[0][0], self.points[0][1]+level]]

        pygame.draw.polygon(self.window, self.COLORS['green'], points)


