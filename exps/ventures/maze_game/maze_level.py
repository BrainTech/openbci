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

from constants.constants_levels import LEVELS_IN_ORDER,LEVELS_IN_ORDER_T, LEVELS_GAME_TIMEOUT, LEVELS_TRAINING, LEVELS_TRAINING_TIMEOUT, LEVELS_GAME

class MazeLevel(object):
    def __init__(self, session_type):
        super(MazeLevel, self).__init__()
        self.x = 0
        self.y = 0

        if session_type=='training':
            self.level_in_order = LEVELS_IN_ORDER_T
            self.level_timeout = LEVELS_TRAINING_TIMEOUT
            self.levels_maze = LEVELS_TRAINING
        elif session_type == 'experiment':
            self.level_in_order = LEVELS_IN_ORDER
            self.level_timeout = LEVELS_GAME_TIMEOUT
            self.levels_maze = LEVELS_GAME

    def _init_level_arrays(self, level):
        
        self.level = np.zeros((len(level), len(level[0])))
        self.level_path = np.zeros((len(level), len(level[0])))
        for y_ind, level_line in enumerate(level):
            for x_ind, level_value in enumerate(level_line):
                if type(level_value) == tuple:
                    level_array_part = level_value[0]
                    level_path_part = level_value[1]
                    self.level[y_ind][x_ind] = level_array_part
                    self.level_path[y_ind][x_ind] = level_path_part
                else:
                    if level_value in [1, 2, 3, 4]:
                        if level_value == 3:
                            self.level[y_ind][x_ind] = level_value
                            self.level_path[y_ind][x_ind] = -1
                        elif level_value == 4:
                            self.level[y_ind][x_ind] = level_value
                            self.level_path[y_ind][x_ind] = -2
                        else:
                            self.level[y_ind][x_ind] = level_value

    def _init_path(self):
        self.path = {}
        number_points = np.max(self.level_path)
        self.path_points = ['']*(number_points+2)
        for y_ind, level_path_line in enumerate(self.level_path):
            for x_ind, level_path_value in enumerate(level_path_line):
                if level_path_value > 0:
                    self.path_points[int(level_path_value)] = (y_ind, x_ind)
                elif level_path_value == -1:
                    self.position_start = (y_ind, x_ind)
                    self.path_points[0] = (y_ind, x_ind)
                elif level_path_value == -2:
                    self.path_points[-1] = (y_ind, x_ind)
                    self.position_finish = (y_ind, x_ind)

        for ind in range(1, len(self.path_points)):
            if self.path_points[ind-1][1] == self.path_points[ind][1]:
                axis_range = np.sort([self.path_points[ind-1][0], self.path_points[ind][0]])
                path = [(y, self.path_points[ind][1]) for y in range(axis_range[0], axis_range[1]+1)]
                if self.path_points[ind-1][0]>self.path_points[ind][0]:
                    path.reverse()

            elif self.path_points[ind-1][0] == self.path_points[ind][0]:
                axis_range = np.sort([self.path_points[ind-1][1], self.path_points[ind][1]])
                path = [(self.path_points[ind][0], x) for x in range(axis_range[0], axis_range[1]+1)]
                if self.path_points[ind-1][1]>self.path_points[ind][1]:
                    path.reverse()

            self.path[self.path_points[ind-1]] = path 
            
    def _init_path_point(self):
        path = []
        point = self.get_position_start()
        while point != self.get_position_finish():
            path.append(self.path[point])
            point = self.path[point][-1]
        print path
        self.all_path_points = path
        self.left_path_points = sum(path, [])
        print self.left_path_points

    def load_level(self, level_number):
        print str(self.level_in_order[int(level_number)])
        level, level_type =  self.levels_maze[str(self.level_in_order[int(level_number)])], 'n'
	print level, level_type, level_number
        self._init_level_arrays(level)
        if level_type == 'T':
            self.level = self.level.T
            self.level_path = self.level_path.T
        elif level_type == 'T->':
            self.level = np.array([row[::-1] for row in self.level]).T
            self.level_path = np.array([row[::-1] for row in self.level_path]).T
        self._init_path()
        self._init_path_point()
        self._set_ball_position_start()

    def _set_ball_position_start(self):
        ly, lx = self.get_position_start()
        self.set_ball_x(lx)
        self.set_ball_y(ly)

    def get_level_array(self):
        return self.level

    def get_all_path(self):
        return sum(self.all_path_points, [])

    def get_path_left(self):
        for ind, point in enumerate(self.left_path_points):
            if point == (self.get_ball_y(), self.get_ball_x()):
                self.left_path_points = self.left_path_points[ind:]
                return self.left_path_points
        return []

    def get_active_path(self):
        for step, points in enumerate(self.all_path_points):
            for ind, point in enumerate(points[:-1]):
                if point == (self.get_ball_y(), self.get_ball_x()):
                    try:
                        return sum([self.all_path_points[step][ind:],self.all_path_points[step+1]], [])
                    except IndexError:
                        return self.all_path_points[step][ind:]
        return []

    def get_position_start(self):
        return self.position_start

    def get_position_finish(self):
        return self.position_finish

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
        return len(self.level_in_order)
