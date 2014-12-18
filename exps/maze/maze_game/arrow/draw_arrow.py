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

    def __init__(self, window, type_, arrow_colors_levels, 
                 proportion = [37.5, 37.5, 25.0], size = 120,
                 levels_lines = True):
        super(DrawArrow, self).__init__()
        self.window = window
        if type_ == 'right':
            self.arrow = RightArrow(arrow_colors_levels, proportion, size, levels_lines)

        elif type_ == 'left':
            self.arrow = LeftArrow(arrow_colors_levels, proportion, size, levels_lines)

        elif type_ == 'up':
            self.arrow = UpArrow(arrow_colors_levels, proportion, size, levels_lines)

        elif type_ == 'down':
            self.arrow = DownArrow(arrow_colors_levels, proportion, size, levels_lines)

        self.level = 0

    def _draw_black_shape_arrow(self):
        line1, line2 = self.arrow.get_shape_level_points()

        if self.arrow.are_levels_lines():
            pygame.draw.line(self.window, self.COLORS['black'], line1[0], line1[1], 2)
            pygame.draw.line(self.window, self.COLORS['black'], line2[0], line2[1], 2)

        pygame.draw.polygon(self.window, self.COLORS['black'], self.arrow.points, 3)

    def _draw_level_data(self, level, points, color):
        pygame.draw.polygon(self.window, self.COLORS[color], points)
        if level<self.arrow.get_size():
            line = self.arrow.get_level_line_points(level)
            pygame.draw.line(self.window, self.COLORS['black'], line[0], line[1], 2)

    def _draw_white_fill_arrow(self):
        pygame.draw.polygon(self.window, self.COLORS['white'], self.arrow.points)

    def init_position(self, position):
        self.arrow.init_shape(position)

    def init_draw_arrow(self):
        self._draw_white_fill_arrow()
        self._draw_black_shape_arrow()

    def draw_level(self, level):
        color, points = self.arrow.get_level_points(level)
        self._draw_white_fill_arrow()
        self._draw_level_data(level, points, color)
        self._draw_black_shape_arrow()

    def set_level(self, level):
        self.level=level

    def get_level(self):
        return self.level

    def display(self):
        pygame.display.flip()


