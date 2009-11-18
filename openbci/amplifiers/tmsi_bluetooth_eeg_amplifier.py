#!/usr/bin/env python
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2009 Krzysztof Kulewski
#
# Project home: OpenBCI.com
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

"""
TMSi amplifier support.
"""

__author__ = "kulewski@gmail.com (Krzysztof Kulewski)"

import serial, variables_pb2, time
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client
import tmsi


class TMSiBluetoothEEGAmplifier:
    """
    Main class implementing TMSi Bluetooth EEG Amplifier support.
    """
    def __init__(self):
        self.connection = connect_client(type = peers.AMPLIFIER)
        device_name = self.connection.query(message="TMSiDeviceName", \
            type=types.DICT_GET_REQUEST_MESSAGE).message
        self.sampling_rate = int(self.connection.query(message="SamplingRate", \
            type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.channel_numbers = [int(x) for x in \
            self.connection.query(message="AmplifierChannelsToRecord", \
                type=types.DICT_GET_REQUEST_MESSAGE).message.split(" ")]
        self.device = serial.Serial(device_name, baudrate=230400, \
            timeout=3)
        self.vldelta = False
        self.hardware_number_of_channels = -1
        self.vldelta_info = None

    def start_amplifier(self):
        """
        Turns amplifier into straming mode.
        """
        # clean buffer
        self.device.read(10000000)

        # send FrontendInfoRequest
        self.device.write(tmsi.Packet.construct( \
            tmsi.PACKET_TYPE.TMS_FRONTEND_INFO_REQUEST).get_raw())

        # receive FrontendInfo
        frontend_info = tmsi.FrontendInfo.read_one(self.device)
        # store number of channels
        self.hardware_number_of_channels = \
            frontend_info.get_number_of_data_channels()
        # detect if vl delta is needed
        if self.hardware_number_of_channels > 2 and self.sampling_rate > 128:
            self.vldelta = True
            # obtain vl delta info
            vldelta_info_request = tmsi.Packet.construct( \
                tmsi.PACKET_TYPE.TMS_VL_DELTA_INFO_REQUEST)
            self.device.write(vldelta_info_request.get_raw())
            self.vldelta_info = tmsi.VLDeltaInfo.read_one(self.device)
            # we have to multiply sampling rate by 2 - because channels are sent
            # 2x slower (channels 1-24)
            self.sampling_rate = self.sampling_rate * 2
        # set sample rate
        frontend_info.modify_sample_rate(self.sampling_rate)
        # turn on amplifier
        frontend_info.start()
        # send corrected frontend info back into amplifier
        frontend_info.recalculate_checksum()
        self.device.write(frontend_info.get_raw())

        # receive ack and check its status
        ack = tmsi.Acknowledge.read_one(self.device)
        if ack.is_error():
            assert False, "Acknowledge error: " + ack.get_error()

        return self


    def do_sampling(self):
        """
        Start sending samples forever.
        """
        last_keep_alive = time.time()
        while True:
            try:
                timestamp = time.time()
                if self.vldelta:
                    data = tmsi.VLDeltaData.read_one(self.device, search=True)
                    data.set_vldelta_info(self.vldelta_info)
                else:
                    data = tmsi.ChannelData.read_one(self.device, search=True)
                data.set_number_of_channels(self.hardware_number_of_channels)
                channel_data = data.decode()
            
                if data.on_off_pressed():
                    print "Digi: On/Off button is pressed"
                if data.trigger_active():
                    print "Digi: Trigger active"
                if data.battery_low():
                    print "Digi: Battery is low"
            
                # send samples
                for i in range(len(channel_data[0])):
                    sample_vector = variables_pb2.SampleVector()
                    for j in self.channel_numbers:
                        samp = sample_vector.samples.add()
                        samp.value = float(channel_data[j][i])
                        samp.timestamp = timestamp
                    self.connection.send_message( \
                        message=sample_vector.SerializeToString(), \
                        type=types.AMPLIFIER_SIGNAL_MESSAGE, flush=True)
                    if i != len(channel_data[0]) - 1:
                        # if this is not the last sample we want to send
                        # this implies that we are decoding vldelta packet
                        # then we want to send samples with self.sampling_rate/2
                        # frequency (/2 because before we multiplied it by *2),
                        # so we want to wait 2./self.sampling_rate seconds
                        # after last sample we don't want to sleep - it will be
                        # done in next read call
                        time.sleep(2./self.sampling_rate)                
                # send keep alive if there was 10s before previous ack
                if timestamp - last_keep_alive > 10:
                    last_keep_alive = timestamp
                    self.device.write(tmsi.Packet.construct( \
                        tmsi.PACKET_TYPE.TMS_KEEP_ALIVE).get_raw())
            except AssertionError, exception:
                if str(exception) == "Invalid checksum":
                    # silently ignore such samples
                    print "Received packet with wrong checksum"
                else:
                    raise exception
                

if __name__ == "__main__":
    TMSiBluetoothEEGAmplifier().start_amplifier().do_sampling()

