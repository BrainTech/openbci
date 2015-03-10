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
from constants.constants_wii_levels import AREA_SIZE, STEP_UP, STEP_DOWN, LEVELS_NUMBER

class MazeWiiLevel(object):
    def __init__(self, session_type, wii_level_params):
        super(MazeWiiLevel, self).__init__()
        self.session_type = session_type
        # print "WII_LEVEL_PARAMS:", str(wii_level_params)
        self._init_wii_level_params(wii_level_params)
        # self.level_params = {'right':{'step_up':STEP_UP, 'step_down':STEP_DOWN, 'area_start_value':30, 'area_end_value':100},
        #                      'left' :{'step_up':STEP_UP, 'step_down':STEP_DOWN, 'area_start_value':30, 'area_end_value':100},
        #                      'down' :{'step_up':STEP_UP, 'step_down':STEP_DOWN, 'area_start_value':30, 'area_end_value':100},
        #                      'up'   :{'step_up':STEP_UP, 'step_down':STEP_DOWN, 'area_start_value':30, 'area_end_value':100}}
        #self._init_wii_level_params(wii_level_params)
        #min, max,  *calib4direct



    # def _get_area_value(self, level, motor_step, motor_initial, session_number):
    #     pass
        # print level, motor_step, motor_initial, session_number
        # level = level + (motor_initial + session_number - 1) * motor_step
        # return level-(AREA_SIZE/2), (level+AREA_SIZE/2), level
    def _get_area_value(self, level, direction):
        # print '_________________get_area_value_____________________________'
        # print '__________________step:', self.step
        l = self.start_points[direction]+self.step*level
        return l-(AREA_SIZE/2), (l+AREA_SIZE/2), l


    def _init_wii_level_params(self, wii_level_params):
        # print '________________init params_____________________________'
        self.step = (wii_level_params['motor_max_level'] - wii_level_params['motor_min_level'])/LEVELS_NUMBER
        self.start_points = {'right':wii_level_params['right']+wii_level_params['motor_min_level'],
                             'left' :wii_level_params['left']+wii_level_params['motor_min_level'],
                             'down' :wii_level_params['down']+wii_level_params['motor_min_level'],
                             'up'   :wii_level_params['up']+wii_level_params['motor_min_level']}

        self.level_params = {'right':{'step_up':STEP_UP, 'step_down':STEP_DOWN},
                             'left' :{'step_up':STEP_UP, 'step_down':STEP_DOWN},
                             'down' :{'step_up':STEP_UP, 'step_down':STEP_DOWN},
                             'up'   :{'step_up':STEP_UP, 'step_down':STEP_DOWN}}
    #     for direction in ['right', 'left', 'up', 'down']:
    #         area_start_value, area_end_value, level = self._get_area_value(wii_level_params[direction], 
    #                                                                        wii_level_params['motor_step'],
    #                                                                        wii_level_params['motor_initial'], 
    #                                                                        wii_level_params['session_number'])    
    #         self.level_params[direction]['area_start_value'] = area_start_value
    #         self.level_params[direction]['area_end_value'] = area_end_value
    #         self.level_params[direction]['level'] = level

    def get_level(self, direction):
        # print "********************************GET_ {} *************************".format(direction)
        return (self.level_params[direction]['step_up'], 
                self.level_params[direction]['step_down'], 
                self.level_params[direction]['area_start_value'],
                self.level_params[direction]['area_end_value'])

    def get_levels(self):
        return (self.level_params['up']['level'], 
                self.level_params['down']['level'], 
                self.level_params['left']['level'],
                self.level_params['right']['level'])

    def load_level(self, direction, level):
        area_start_value, area_end_value, area_level = self._get_area_value(level, direction)
        # print 
        self.level_params[direction]['area_start_value'] = area_start_value
        self.level_params[direction]['area_end_value'] = area_end_value
        self.level_params[direction]['level'] = area_level
        # print "********************************LOAD_{} _{}, {}, {}, {}*************************".format(direction, level, area_start_value, area_end_value, area_level)
        pass
        #znien level