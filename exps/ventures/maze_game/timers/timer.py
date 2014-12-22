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

import time

class Timer(object):
    def __init__(self, timer_duration, time_left_out=0):
        super(Timer, self).__init__()
        self.timer_duration = timer_duration
        self.time_left_out = time_left_out
        self.pause_duration = 0
    
    def run(self):
        self.time_start = time.time()

    def stop(self):
        self.time_stop = time.time()

    def get_time_length(self):
        return self.time_stop - self.time_start - self.pause_duration

    def get_timer_status(self):
        if self.timer_duration-(time.time()-self.time_start + self.time_left_out - self.pause_duration) > 0:
            return True

        else:
            return False

    def make_pause(self):
        self.pause_start = time.time()

    def finish_pause(self):
        self.pause_duration+= time.time() - self.pause_start

    def get_timer_time(self):
        time_ = self.timer_duration - (time.time()- self.time_start - self.pause_duration)

        if time_ > 0:
        	return '{:0>2d}:{:0>2d}'.format(int(time_/60), int(time_%60))
        else:
        	return '{:0>2d}:{:0>2d}'.format(0, 0)

    def get_time_start(self):
        return self.time_start

    def get_time_stop(self):
        return self.time_stop