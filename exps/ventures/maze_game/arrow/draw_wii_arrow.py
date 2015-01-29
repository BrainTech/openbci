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

from draw_arrow import DrawArrow

class DrawWiiArrow(DrawArrow):
    def __init__(self, window, type_, arrow_colors_levels, 
                 proportion = [37.5, 37.5, 25.0], size = 120,
                 levels_lines = True):
        super(DrawWiiArrow, self).__init__(window, type_, arrow_colors_levels, 
                                           proportion, size, levels_lines)

    def _draw_wii_area_data(self, area_param):
        (point1, point2), (point3, point4) = self.arrow.get_shape_level_points()
        color = self._get_area_color(area_param)
        pygame.draw.polygon(self.window, color, (point1, point2, point3, point4))
        pygame.draw.line(self.window, self.COLORS['black'], point1, point2, 2)
        pygame.draw.line(self.window, self.COLORS['black'], point3, point4, 2)


    def _draw_level_data(self, level, points, color):
        if level<self.arrow.get_size():
            line = self.arrow.get_level_line_points(level)
            pygame.draw.line(self.window, self.COLORS['yellow'], line[0], line[1], 2)

    def _get_area_color(self, area_param):
        value = 255-int((float(area_param)/100)*255)
        return (value, 255, value)

    def set_arrow_proportion(self, proportion):
        self.arrow.set_levels(proportion)

    def draw_level(self, level, area_param):
        level = 100*(float(level)/self.size)
        color, points = self.arrow.get_level_points(level)
        self._draw_white_fill_arrow()
        self._draw_wii_area_data(area_param)
        self._draw_level_data(level, points, color)
        self._draw_black_shape_arrow()
