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

import serial, variables_pb2, time
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client


class TMSiEEGAmplifier:
    def __init__(self):
        self.connection = connect_client(type = peers.AMPLIFIER)
        self.device_name = self.connection.query(message="TMSiDeviceName", type=types.DICT_GET_REQUEST_MESSAGE).message
        self.sampling_rate = int(self.connection.query(message="SamplingRate", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.channel_numbers = [int(x) for x in \
            self.connection.query(message="AmplifierChannelsToRecord", type=types.DICT_GET_REQUEST_MESSAGE).message.split(" ")]
        self.device = serial.Serial(self.device_name, baudrate=230400, timeout=3)

    
    # oblicza sume kontrolna zadanego ciagu bajtow		
    # traktujac data jako liste dwubajtowych slow, sumuje je, a nastepnie zwraca negacje sumy
    def _calculate_cheksum(self, data):
        a = 0
        for i in range(len(data)):
            a = (a + ord(data[i]) * 256 ** (i % 2)) % 65536
        a = 65536 - a
        return chr(a % 256) + chr(a / 256)


    # oblicza sume kontrolna zadanego ciagu bajtow i dokleja ja na jego koniec
    def calculate_cheksum(self, data):
        return data + self._calculate_cheksum(data)


    def extract_channel_data(self, data, channel_number):
        return ord(data[4 + 3 * channel_number]) + \
               ord(data[5 + 3 * channel_number]) * 256 + \
               ord(data[6 + 3 * channel_number]) * 65536 - \
               (2 ** 24 if ord(data[6 + 3 * channel_number]) > 128 else 0)


    def start_amplifier(self):
        # clean buffer
        self.device.read(10000000)

        # send FrontendInfoRequest
        self.device.write(self.calculate_cheksum("\xaa\xaa\x00\x03"))

        # receive FrontendInfo
        response = self.device.read(38)

        # prepare FrontendInfo with answer
        response_bits = list(response)
        # modify bits responsible for streaming
        response_bits[8] = "\x02"
        # drop previous checksum
        response_bits = response_bits[:-2]
        
        # send it
        self.device.write(self.calculate_cheksum("".join(response_bits)))

        # receive ack
        self.device.read(10)

        return self


    def do_sampling(self):
        data = []
        offset = 0
        while True:
            # read one frame
            data = self.device.read(14)
            timestamp = time.time()
	    data = list(data)
            # skip bad data at the beginning and read a better one
            while data[0] != '\xaa' or data[1] != '\xaa':
                data = data[1:]
                data.append(self.device.read(1))
            
            offset += 1

            # now data should have correct header
            assert data[0] == "\xaa"
            assert data[1] == "\xaa"

            channels_data = []
            for channel_number in self.channel_numbers:
                channels_data.append(self.extract_channel_data(data, channel_number))
           
            sampleVector = variables_pb2.SampleVector()
            
            for x in channels_data:
                samp = sampleVector.samples.add()
                samp.value = float(x)
                samp.timestamp = timestamp
                    
            # channels_data_message = " ".join(str(x) for x in channels_data)
            self.connection.send_message(message=sampleVector.SerializeToString(), type=types.AMPLIFIER_SIGNAL_MESSAGE, flush=True)

            # send keep alive
            if offset % (5 * self.sampling_rate) == 0:
                self.device.write(self.calculate_cheksum("\xaa\xaa\x00\x27"))

if __name__ == "__main__":
    TMSiEEGAmplifier().start_amplifier().do_sampling()

