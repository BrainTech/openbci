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

import Queue
class LogicQueue(object):
    def __init__(self):
        self._queue = Queue.Queue()

    def clear_queue(self):
        print("Clear queue!!!")
        while True:
            try:
                self._queue.get_nowait()
            except Queue.Empty:
                break

    def handle_message(self, msg):
        try:
            self._queue.put_nowait(msg)
        except Queue.Full:
            print("Warning! Queue is full. Drop message!!!")
    
    def get_message(self):
        if self._queue.qsize() > 2:
            print("Warning! Queue size is: "+str(self._queue.qsize()))
        try:
            return self._queue.get_nowait()
        except Queue.Empty:
            return None
