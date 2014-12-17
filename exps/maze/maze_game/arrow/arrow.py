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
    def __init__(self, levels):
        super(Arrow, self).__init__()
        self.levels = levels

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
        if level<self.levels[0]:
            return 'yellow'
        elif level<= self.levels[1]:
            return 'green'
        else:
            return 'red'
