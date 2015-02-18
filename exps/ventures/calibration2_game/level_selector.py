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

import pygame, time
from pygame.locals import *
pygame.mixer.init()
from obci.exps.ventures import logic_queue


class BinaryManager(object):
    def __init__(self, start, end):
        self._start = start
        self._end = end

    def get_current(self):
        
        """Return current, last where:
        - current is a  middle or bigger-closest-to-middle 
          between self._start and self._end
        - last is true if self._end - self._start == 0 or 1,
          which implicates that current == self._end == self._start
          or current == self._end == self._start + 1
        """
        self._current = self._start + (self._end  - self._start + 1)/2
        last = self._current == self._end
        return self._current, last

    def cutoff_above(self):
        self._end = self._current - 1

    def cutoff_below(self):
        self._start = self._current + 1

class LevelSelector(object):
    """This class should be used in specific manner:
    after every get_level() single update_level_result() should be fired
    The class implement following algorithm:
    - perform binary search in self._levels, 
      while selecting cutoff half according to update_level_result incoming value
    - if binary search is done and update_level_result still gets false
      peroform linear search, every time one step down
    """
    def __init__(self, levels):
        self._binary_manager = BinaryManager(0, len(levels)-1)
        # a list of integers
        self._levels = levels
        #'binary' for binary selection mode, 'sequential for sequential downstep mode
        self._mode = 'binary'
        #true if binary selection has just finished 
        self._last = False
        #index of currently returned value in get_level
        self._ind = -1

    def get_level(self):
        """Return 'appropriate' value from self._levels (int)"""
        if self._mode == 'binary':
            ind, last = self._binary_manager.get_current()
            self._last = last
            self._ind = ind
        else: #mode == 'sequential'
            self._ind -= 1
        return self._levels[self._ind]

    def update_level_result(self, result):
        """Return:
        - 0 to note that the algorithm needs to run more trials
        - 1 to note that the algorithm should end gracefully
        - 2 to note that the there is sth wrong becouse we reached the beginning of self._levels
          and still we don't have a result
        """
        if self._mode == 'binary':
            if self._last:
                if result:
                    return 1
                else:
                    if self._ind == 0:
                        return 2
                    else:
                        self._mode = 'sequential'
                        return 0
            else:
                if result:
                    self._binary_manager.cutoff_below()
                else:
                    self._binary_manager.cutoff_above()
                return 0
        else: #mode == 'sequential'
            if result:
                return 1
            else:
                if self._ind == 0:
                    return 2
                else:
                    return 0
