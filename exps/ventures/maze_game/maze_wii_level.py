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
from constants.constants_wii_levels import WII_LEVELS

class MazeWiiLevel(object):
    def __init__(self, sesion_type):
        super(MazeWiiLevel, self).__init__()
        self.sesion_type = sesion_type
        self._init_level_params()

    def _init_level_params(self):
        self.level_params = {}
        self.level_params['left'] = ''
        self.level_params['right'] = ''
        self.level_params['down'] = ''
        self.level_params['up'] = ''

    def get_level(self, direction):
        return (self.level_params[direction]['step_up'], 
                self.level_params[direction]['step_down'], 
                self.level_params[direction]['area_start_value'],
                self.level_params[direction]['area_end_value'])

    def load_level(self, direction, level):
        print "LOAD NEW LEVEL!:", level, direction
        try:
            self.level_params[direction] = WII_LEVELS[str(level)]
        except KeyError:
            self.level_params[direction] = WII_LEVELS[str(1)]

        print self.level_params[direction]