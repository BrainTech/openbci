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

from right_arrow import RightArrow 
from left_arrow import LeftArrow 
from up_arrow import UpArrow 
from down_arrow import DownArrow 

class DrawArrow(object):
    COLORS = {'black'  : (  0,   0,   0),
              'white'  : (255, 255, 255),
              'yellow' : (255, 255,   0),
              'green'  : (  0, 255,   0),
              'red'    : (255,   0,   0)}

    def __init__(self, window, type_, levels=[45,90]):
        super(DrawArrow, self).__init__()
        self.window = window
        if type_ == 'right':
            self.arrow = RightArrow(levels)
        elif type_ == 'left':
            self.arrow = LeftArrow(levels)
        elif type_ == 'up':
            self.arrow = UpArrow(levels)
        elif type_ == 'down':
            self.arrow = DownArrow(levels)
        self.level=0

    def init_position(self, position):
        self.arrow.init_shape(position)

    def draw_black_shape_arrow(self):
        line1, line2 = self.arrow.get_shape_level_points()
        if self.arrow.levels[0]>0:
            pygame.draw.line(self.window, self.COLORS['black'], line1[0], line1[1], 2)
        if self.arrow.levels[1]<120:
            pygame.draw.line(self.window, self.COLORS['black'], line2[0], line2[1], 2)
        pygame.draw.polygon(self.window, self.COLORS['black'], self.arrow.points, 3)

    def draw_white_fill_arrow(self):
        pygame.draw.polygon(self.window, self.COLORS['white'], self.arrow.points)

    def init_draw_arrow(self):
        self.draw_white_fill_arrow()
        self.draw_black_shape_arrow()

    def draw_level(self, level):
        color, points = self.arrow.get_level_points(level)
        self.draw_white_fill_arrow()
        pygame.draw.polygon(self.window, self.COLORS[color], points)
        self.draw_black_shape_arrow()
        self.display()

    def set_level(self, level):
        self.level=level

    def get_level(self):
        return self.level

    def display(self):
        pygame.display.flip()


