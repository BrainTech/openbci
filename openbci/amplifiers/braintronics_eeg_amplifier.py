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

import time
import serial
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client


class BraintronicsEEGAmplifier:
    def __init__(self):
        self.connection = connect_client(type = peers.AMPLIFIER)
        self.device_name = self.connection.query(message="BraintronicsDeviceName", type=types.DICT_GET_REQUEST_MESSAGE).message
        self.channel_numbers = [int(x) for x in \
            self.connection.query(message="AmplifierChannelsToRecord", type=types.DICT_GET_REQUEST_MESSAGE).message.split(" ")]
        self.device = serial.Serial(self.device_name, baudrate=921600, timeout=3)

    
    def extract_channel_data(self, data, channel_number):
        return ord(data[4 + 2 * channel_number]) + \
               ord(data[5 + 2 * channel_number]) * 256 - \
               (2 ** 16 if ord(data[5 + 2 * channel_number]) > 128 else 0)


    def start_amplifier(self):
        # clean buffer
        self.device.read(10000000)

        # send start command
        self.device.write("\x53\xAC\x03\xFC\x68\x97")

        # magic sleep
        time.sleep(0.05)
        
        return self


    def do_sampling(self):
        data = ""
        offset = 0
        start = True
        while True:
            # read one frame
            
            data = self.device.read(132)
            
            # skip bad data at the beginning and read a better one
            if start and data[0] != '\t':
                data = data[1:]
                data.append(self.device.read(1))
            
            start = False

            # now data should have correct header
            assert data[0] == '\xff'
            assert data[1] == '\xff'
            assert ord(data[3]) * 256 + ord(data[2]) == offset
            
            offset += 1

            channels_data = []
            for channel_number in self.channel_numbers:
                channels_data.append(self.extract_channel_data(data, channel_number))
            channels_data_message = " ".join(str(x) for x in channels_data)
            self.connection.send_message(message=channels_data_message, type=types.AMPLIFIER_SIGNAL_MESSAGE, flush=True)
            
            # sleep not to ask amp to often - just 125 times per second for now
            time.sleep(0.05)



if __name__ == "__main__":
    BraintronicsEEGAmplifier().start_amplifier().do_sampling()

