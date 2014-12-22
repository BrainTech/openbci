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

from timer import Timer

class LevelWatcher(Timer):
    def __init__(self, timer_duration):
        super(LevelWatcher, self).__init__(timer_duration)
        self.level_fail = 0

    def report_level_fail(self):
        self.level_fail += 1

    def can_level_repeat(self):
        if self.level_fail < 3 and self.get_timer_status():
            return True
        else:
            return False

    def get_level_fail(self):
        return self.level_fail
