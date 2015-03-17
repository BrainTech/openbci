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

class DrawBox(object):
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
              'green_2': (0, 255, 0)}

    def __init__(self, window):
        super(DrawBox, self).__init__()
        self.window = window
        self.points = None

    def _display(self): 
        pygame.display.flip()

    def init_box(self, direction, level_min, level_max):
        if direction == 'left':
            self.points = [[self.BLOCK_TYPE[direction][0][0]-level_min,self.BLOCK_TYPE[direction][0][1]+2],
                      [self.BLOCK_TYPE[direction][1][0]-level_min, self.BLOCK_TYPE[direction][1][1]-2],
                      [self.BLOCK_TYPE[direction][1][0]-level_max, self.BLOCK_TYPE[direction][1][1]-2],
                      [self.BLOCK_TYPE[direction][0][0]-level_max, self.BLOCK_TYPE[direction][0][1]+2]]

        elif direction =='right':

            self.points = [[self.BLOCK_TYPE[direction][0][0]+level_min, self.BLOCK_TYPE[direction][0][1]+2], 
                      [self.BLOCK_TYPE[direction][1][0]+level_min, self.BLOCK_TYPE[direction][1][1]-2], 
                      [self.BLOCK_TYPE[direction][1][0]+level_max, self.BLOCK_TYPE[direction][1][1]-2],
                      [self.BLOCK_TYPE[direction][0][0]+level_max, self.BLOCK_TYPE[direction][0][1]+2]]

        elif direction =='up':
            self.points = [[self.BLOCK_TYPE[direction][0][0]-2, self.BLOCK_TYPE[direction][0][1]-level_min], 
                      [self.BLOCK_TYPE[direction][1][0]+2, self.BLOCK_TYPE[direction][1][1]-level_min],  
                      [self.BLOCK_TYPE[direction][1][0]+2, self.BLOCK_TYPE[direction][1][1]-level_max],
                      [self.BLOCK_TYPE[direction][0][0]-2, self.BLOCK_TYPE[direction][0][1]-level_max]]

        elif direction =='down':
           self.points = [[self.BLOCK_TYPE[direction][0][0]-2, self.BLOCK_TYPE[direction][0][1]+level_min], 
                      [self.BLOCK_TYPE[direction][1][0]+2, self.BLOCK_TYPE[direction][1][1]+level_min],  
                      [self.BLOCK_TYPE[direction][1][0]+2, self.BLOCK_TYPE[direction][1][1]+level_max],
                      [self.BLOCK_TYPE[direction][0][0]-2, self.BLOCK_TYPE[direction][0][1]+level_max]]
        
        #pygame.draw.polygon(self.window, self.COLORS['white'], self.points)
        pygame.draw.polygon(self.window, self.COLORS['gray'], self.points, 4)
        pygame.draw.polygon(self.window, self.COLORS['green_2'], self.points, 2)
        self._display()

    def _get_area_color(self, area_param):
        value_0 = 255-int((float(area_param)/100)*(255-(self.COLORS['green'][0])))
        value_2 = 255-int((float(area_param)/100)*(255-(self.COLORS['green'][2])))
        return (value_0, self.COLORS['green'][1], value_2)

    def update_box(self, area_param):
        pygame.draw.polygon(self.window, self._get_area_color(area_param), self.points)
        pygame.draw.polygon(self.window, self.COLORS['gray'], self.points, 4)
        pygame.draw.polygon(self.window, self.COLORS['green_2'], self.points, 2)

    def draw_box_color(self, color):
        pygame.draw.polygon(self.window, self.COLORS[color], self.points)
        pygame.draw.polygon(self.window, self.COLORS['gray'], self.points, 4)
        pygame.draw.polygon(self.window, self.COLORS['green_2'], self.points, 2)
