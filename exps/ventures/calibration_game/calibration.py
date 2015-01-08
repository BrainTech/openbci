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
pygame.mixer.init()

from calibration_screen import CalibrationScreen

class Calibration(object):
    def __init__(self):
        super(Calibration, self).__init__()
        self.screen = CalibrationScreen()
        self.level1 = 0
        self.level2 = 0
        self.level3 = 0
        self.level4 = 0

    def run(self):
        done = False
        while not done:
            for event in pygame.event.get():                  
                if event.type == QUIT:
                    self.finish_calibration()
                    done = True

                elif event.type == KEYDOWN:            
                    if event.key == K_ESCAPE:
                        self.finish_calibration()
                        done = True
                    if event.key == K_RIGHT:
                        self.level1 = (self.level1+1)#%200
                        print self.level1
                        self.screen.update_block('right', self.level1)
                    if event.key == K_LEFT:
                        self.level2 = (self.level2+1)#%200
                        print self.level2
                        self.screen.update_block('left', self.level2)
                    if event.key == K_UP:
                        self.level3 = (self.level3+1)#%200
                        print self.level3
                        self.screen.update_block('up', self.level3)
                    if event.key == K_DOWN:
                        self.level4 = (self.level4+1)#%200
                        print self.level4
                        self.screen.update_block('down', self.level4)


    def finish_calibration(self):
        pygame.quit()


if __name__ == '__main__':
    Calibration().run()

        