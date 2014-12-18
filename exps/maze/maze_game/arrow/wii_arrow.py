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

class WiiArrow(object):
    def __init__(self, direction):
        super(WiiArrow, self).__init__()
        self.direction = direction
        self.arrow_level = 0
        self.area_state = 0

    def get_area_state(self):
        return self.area_state

    def get_arrow_level(self):
        return self.arrow_level

    def set_level(self, step_up, step_down, area_start_value, area_end_value):
        self.step_up = step_up
        self.step_down = step_down
        self.area_start_value = area_start_value
        self.area_end_value = area_end_value

    def _update_arrow_level(self, value):
        self.arrow_level = value
    
    def _increase_area_state(self):
        if self.area_state + self.step_up >= 100:
            self.area_state =100
        else:
            self.area_state += self.step_up

    def _dicrease_area_state(self):
        if self.area_state < self.step_down:
            self.area_state =0
        else:
            self.area_state -= self.step_down
    def _update_area_state(self, value):
        if value > self.area_start_value and value < self.area_end_value:
            self._increase_area_state()
        else:
            self._dicrease_area_state()

    def update(self, value):
        self._update_arrow_level(value)
        self._update_area_state(value)

    def _reset_area_state(self):
        self.area_state = 0

    def _reset_arrow_level(self):
        self.arrow_level = 0

    def reset(self):
        self._reset_area_state()
        self._reset_arrow_level()

    def is_move(self):
        if self.area_state == 100:
            return True
        else:
            return False
        