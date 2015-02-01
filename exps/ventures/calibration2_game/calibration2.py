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
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

import pygame, time, sys
from pygame.locals import *
pygame.mixer.init()
from obci.exps.ventures import logic_queue
from level_selector import LevelSelector
from calibration_screen_2 import CalibrationScreen2 as CalibrationScreen
from obci.exps.ventures.maze_game.arrow.wii_arrow import WiiArrow as CalibBox

class Calibration2(logic_queue.LogicQueue):
    """
    - perform calibration2 logic (display boxes in specific order)
    - optinally perform 'final check' on 4 selected boxes
    - store selected boxes (starting levels for 4 directions) for user id
    """
    def __init__(self, user_id, boxes_levels):
        """
        - user_id - string
        - boxes_levels - list of integers representing % of max sway; 
          for every this number a box should be generated for tests
        """
        super(Calibration2, self).__init__()
        self._level_selector = {'up': LevelSelector(boxes_levels), 
                                'right': LevelSelector(boxes_levels),
                                'down': LevelSelector(boxes_levels), 
                                'left': LevelSelector(boxes_levels)
                                }
        self.screen = CalibrationScreen()


    def try_calib_box(self, direction, level):
        self.calib_box_state = CalibBox('')
        self.calib_box_state.direction = direction
        self.calib_box_state.set_level(1,1, level-20, level+20)
        self.screen.display_box(direction, level-20, level+20)
        done = False
        self.clear_queue()   
        while not done:
            for event in pygame.event.get():                  
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    return False
            sample = self.get_message()
            if sample is not None:
                if sample.key == direction:
                    self.calib_box_state.update(sample.value)
                else:
                    self.calib_box_state.reset()
                self.screen.update_block(sample.key, sample.value, self.calib_box_state.get_area_state())
                if self.calib_box_state.is_move():
                    self.screen.clear(True)
                    return True


    def run(self):
        done = False
        selected_levels = {'up': None,
                           'right': None,
                           'down': None,
                           'left': None
                       }

        while not done:
            for d in selected_levels.keys():
                if selected_levels[d] is None:
                    level = self._level_selector[d].get_level()
                    passed = self.try_calib_box(d, level)
                    #passed = True #TODO - perform trial on 'level' value in order to determine if patient succeeded in selecting box on level value 'level'
                    res = self._level_selector[d].update_level_result(passed)
                    print("For direction: "+str(d)+" got level: "+str(level)+" and result: "+str(res))
                    if res == 0:
                        #just try again
                        pass
                    elif res == 1:
                        #bingo, level is user's best possible level
                        selected_levels[d] = level
                    elif res == 2:
                        #kind of error - user cant succeede even on easiest level, finish somehow, error or sth. next get_level call would end up badly...
                        pass #TODO
                        print("ERROR 2")
                        sys.exit(1)

            if not (None in selected_levels.values()):
                #all levels selected, optionally check them if needed, 
                #store selected_levels for user_id 
                #and finish gracefully so that logic_experiment can finish gracefully
                pass#TODO
                done = True
                print "Selected levels: "
                print str(selected_levels)

# if __name__ == '__main__':
#     Calibration2().run()

        
