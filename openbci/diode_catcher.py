#!/usr/bin/env python
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
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
#      Krzysztof Kulewski <kulewski@gmail.com>
#      Magdalena Michalska <jezzy.nietoperz@gmail.com>
#



from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, cPickle, collections


class DiodeCatcher(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(DiodeCatcher, self).__init__(addresses=addresses, type=peers.DIODE_CATCHER)
        #self.buffer_size = int(self.conn.query(message="DiodeCatcherBufferSize", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.buffer = collections.deque()

    def handle_message(self, mxmsg):
        if mxmsg.type == types.DIODE_REQUEST:
            if (len(self.buffer) > 0):
                self.send_message(message = self.buffer.popleft(), type = types.DIODE_RESPONSE)
            else:
                self.send_message(message = '', type = types.DIODE_RESPONSE)
        elif mxmsg.type == types.DIODE_MESSAGE:
            
            self.buffer.append(mxmsg.message)
            self.no_response()


if __name__ == "__main__":
    DiodeCatcher(settings.MULTIPLEXER_ADDRESSES).loop()
