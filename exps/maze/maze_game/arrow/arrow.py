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

class Arrow(object):
    def __init__(self, arrow_colors_level=['yellow', 'green', 'red'], 
                 proportion=[37.5, 47.5+37.5, 47.5+37.5+15.0], size=120.0, levels_lines=True):
        super(Arrow, self).__init__()
        self.size = size
        self.set_levels(proportion)
        self.arrow_colors_level = arrow_colors_level
        self.levels_lines = levels_lines

    def set_levels(self, proportion):
        self.levels = [100*(proportion[0]/self.size), 
                       100*((proportion[1])/self.size)]

    def find_point_x(self, x, y, level_x):
        a, b = np.polyfit(x, y, 1)
        return (level_x, level_x*a+b)

    def find_point_y(self, x, y, level_y):
        a, b = np.polyfit(x, y, 1)
        return ((level_y-b)/a, level_y)

    def init_shape(self, position):
        pass

    def get_level_points(self, level):
        pass

    def get_shape_level_points(self):
        pass

    def get_level_color(self, level):
        if level < self.get_level_start_point():
            return self.arrow_colors_level[0]

        elif level <= self.get_level_stop_point():
            return self.arrow_colors_level[1]

        else:
            return self.arrow_colors_level[2]

    def get_size(self):
        return self.size

    def get_level_start_point(self):
        return self.levels[0]

    def get_level_stop_point(self):
        return self.levels[1]

    def are_levels_lines(self):
        return self.levels_lines
