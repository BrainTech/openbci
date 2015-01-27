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
import numpy as np
import random

from constants.constants_levels import LEVELS_IN_ORDER, LEVELS_GAME_TIMEOUT, LEVELS_TRAINING, LEVELS_TRAINING_TIMEOUT

class MazeLevel(object):
    def __init__(self, session_type):
        super(MazeLevel, self).__init__()
        self.x = 0
        self.y = 0

        if session_type=='training':
            self.level_in_order = LEVELS_TRAINING
            self.level_timeout = LEVELS_TRAINING_TIMEOUT
        elif session_type == 'experiment':
            self.level_in_order = LEVELS_IN_ORDER
            self.level_timeout = LEVELS_GAME_TIMEOUT

    def _init_level_arrays(self, level):
        self.level = np.zeros((len(level), len(level[0])))
        self.level_path = np.zeros((len(level), len(level[0])))
        for y_ind, level_line in enumerate(level):
            for x_ind, level_position in enumerate(level_line):
                if type(level_position) == tuple:
                    level_array_part = level_position[0]
                    level_path_part = level_position[1]
                    self.level[y_ind][x_ind] = level_array_part
                    self.level_path[y_ind][x_ind] = level_path_part
                else:
                    if level_position in [1, 2, 3, 4]:
                        if level_position == 3:
                            self.level[y_ind][x_ind] = level_position
                            self.level_path[y_ind][x_ind] = -1
                        elif level_position == 4:
                            self.level[y_ind][x_ind] = level_position
                            self.level_path[y_ind][x_ind] = -2
                        else:
                            self.level[y_ind][x_ind] = level_position

    def _init_path(self):
        self.path = {}

    def load_level(self, level_number):
        level, level_type = self.level_in_order[str(level_number)]
        self._init_level_arrays(level)
        self._init_path()
        if level_type == 'T':
            self.level = np.array(self.level).T
        elif level_type == 'T->':
            self.level = np.array([row[::-1] for row in self.level]).T
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
        return self.level_timeout

    def get_number_of_levels(self):
        return len(self.level_in_order.keys())
