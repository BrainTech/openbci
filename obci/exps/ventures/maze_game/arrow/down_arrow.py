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

import numpy as np
from arrow import Arrow 

class DownArrow(Arrow):
    def __init__(self, arrow_colors_level, proportion, size, levels_lines):
        super(DownArrow, self).__init__(arrow_colors_level, proportion, size, levels_lines)

    def init_shape(self, position):
        point1 = (position[0] - 27, position[1] + 0)
        point2 = (position[0] + 27, position[1] + 0)
        point3 = (position[0] + 27, position[1] + self.get_level_start_point())
        point4 = (position[0] + 68, position[1] + self.get_level_start_point())
        point5 = (position[0] + 0, position[1] + self.get_size())
        point6 = (position[0] - 68, position[1] + self.get_level_start_point())
        point7 = (position[0] - 27, position[1] + self.get_level_start_point())

        self.points = (point1, point2, point3, point4, point5, point6, point7)  

    def get_shape_level_points(self):
        line1_1 = self.points[3]
        line1_2 = self.points[5]

        line2_1 = self.find_point_y([self.points[5][0], self.points[4][0]],
                                    [self.points[5][1], self.points[4][1]],
                                    self.points[0][1] + self.get_level_stop_point())

        line2_2 = self.find_point_y([self.points[4][0], self.points[3][0]],
                                    [self.points[4][1], self.points[3][1]],
                                    self.points[0][1] + self.get_level_stop_point())

        return (line1_1, line1_2), (line2_1, line2_2)

    def get_level_line_points(self, level):
        if level <= self.get_level_start_point():
            return ((self.points[2][0], self.points[0][1] + level),
                   (self.points[6][0], self.points[0][1] + level))

        elif level<self.get_size():
            return (self.find_point_y([self.points[4][0], self.points[3][0]],
                                      [self.points[4][1], self.points[3][1]],
                                      self.points[0][1] + level),
                    self.find_point_y([self.points[5][0], self.points[4][0]],
                                      [self.points[5][1], self.points[4][1]],
                                      self.points[0][1] + level))               

    def get_level_points(self, level):
        if level <= self.get_level_start_point():
            points = (self.points[0], 
                      self.points[1], 
                      (self.points[2][0], self.points[0][1] + level),
                      (self.points[6][0], self.points[0][1] + level))

            return self.get_level_color(level), points

        elif level<self.get_size():
            points = (self.points[0], 
                      self.points[1], 
                      self.points[2], 
                      self.points[3], 
                      self.find_point_y([self.points[4][0], self.points[3][0]],
                                        [self.points[4][1], self.points[3][1]],
                                        self.points[0][1] + level),
                      self.find_point_y([self.points[5][0], self.points[4][0]],
                                        [self.points[5][1], self.points[4][1]],
                                        self.points[0][1] + level),
                      self.points[5], 
                      self.points[6])
            return self.get_level_color(level), points

        else:
            return self.get_level_color(level), self.points