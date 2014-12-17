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
pygame.font.init

import random

from constants.constants_levels import LEVELS_IN_ORDER, LEVELS_TIMEOUT

class MazeLevel(object):
    def __init__(self):
        super(MazeLevel, self).__init__()
        self.x = 0
        self.y = 0

    def load_level(self, level_number):
        self.level = LEVELS_IN_ORDER[str(level_number)]
        self._set_ball_position_start()

    def _set_ball_position_start(self):
        for ly in range(len(self.get_level_array())):
            for lx in range(len(self.get_level_array()[0])):
                if self.get_level_array()[ly][lx] == 3:
                    self.set_ball_x(lx)
                    self.set_ball_y(ly)


    def get_level_array(self):
        return self.level

    def get_ball_x(self):
        return self.x

    def get_ball_y(self):
        return self.y

    def set_ball_x(self, lx):
        self.x = lx

    def set_ball_y(self, ly):
        self.y = ly

    def get_timeout_level(self):
        return LEVELS_TIMEOUT

    def get_levels_quantity(self):
        return len(LEVELS_IN_ORDER.keys())
