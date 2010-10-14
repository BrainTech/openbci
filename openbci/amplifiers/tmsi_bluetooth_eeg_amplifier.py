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

import bluetooth, variables_pb2, time
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client
import tmsi
import gflags
import sys
import re


class TMSiBluetoothEEGAmplifier:
    """
    Main class implementing TMSi Bluetooth EEG Amplifier support.
    """
    def __init__(self, device):
        self.connection = connect_client(type = peers.AMPLIFIER)
        self.sampling_rate = int(self.connection.query(message="SamplingRate", \
            type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.channel_numbers = [int(x) for x in \
            self.connection.query(message="AmplifierChannelsToRecord", \
                type=types.DICT_GET_REQUEST_MESSAGE).message.split(" ")]
        self.device = device
        self.vldelta = False
        self.hardware_number_of_channels = -1
        self.vldelta_info = None

    def start_amplifier(self):
        """
        Turns amplifier into straming mode.
        """

        # send FrontendInfoRequest
        self.device.write(tmsi.Packet.construct( \
            tmsi.PACKET_TYPE.TMS_FRONTEND_INFO_REQUEST).get_raw())

        self.device.prepare(tmsi.PacketType.TMS_FRONTEND_INFO)

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
            self.device.prepare(tmsi.PacketType.TMS_VL_DELTA_INFO)
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

        self.device.prepare(tmsi.PacketType.TMS_ACKNOWLEDGE)

        # receive ack and check its status
        ack = tmsi.Acknowledge.read_one(self.device)
        if ack.is_error():
            assert False, "Acknowledge error: " + ack.get_error()

        return self


    def do_sampling(self):
        """
        Start sending samples forever.
        """
        #if __debug__:
        #    from openbci.core import streaming_debug
        #    self.debug = streaming_debug.Debug(128, LOGGER)

        last_keep_alive = time.time()
        start = time.time()
        while True:
            try:
                timestamp = time.time()
                if self.vldelta:
                    self.device.prepare(tmsi.PacketType.TMS_VL_DELTA_DATA)
                    data = tmsi.VLDeltaData.read_one(self.device, search=True)
                    data.set_vldelta_info(self.vldelta_info)
                else:
                    self.device.prepare(tmsi.PacketType.TMS_CHANNEL_DATA)
                    data = tmsi.ChannelData.read_one(self.device, search=True)
                data.set_number_of_channels(self.hardware_number_of_channels)
                channel_data = data.decode()
            
                if data.on_off_pressed():
                    print "Digi: On/Off button is pressed"
                    var = variables_pb2.Variable()
                    var.key = "Trigger"
                    var.value = "1"
                    #self.connection.send_message( \
                    #    message=var.SerializeToString(), \
                    #    type=types.DICT_SET_MESSAGE, flush=True)

                if data.trigger_active():
                    print "Digi: Trigger active"
                if data.battery_low():
                    print "Digi: Battery is low"
                    var = variables_pb2.Variable()
                    var.key = "AmpBattery"
                    var.value = "0"
                else:
                    var = variables_pb2.Variable()
                    var.key = "AmpBattery"
                    var.value = "1"
                #self.connection.send_message( \
                #        message=var.SerializeToString(), \
                #        type=types.DICT_SET_MESSAGE, flush=True)                     
                                                            
                                                                              

                #print ii/(timestamp - start)
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
                    #if __debug__:
                	#	#Log module real sampling rate
                	#	self.debug.next_sample()
                    #ii += 1
                    if i != len(channel_data[0]) - 1:
                        # if this is not the last sample we want to send
                        # this implies that we are decoding vldelta packet
                        # then we want to send samples with self.sampling_rate/2
                        # frequency (/2 because before we multiplied it by *2),
                        # so we want to wait 2./self.sampling_rate seconds
                        # after last sample we don't want to sleep - it will be
                        # done in next read call
                        pass
                        #time.sleep(2./self.sampling_rate)                
                # send keep alive if there was 10s before previous ack
                if timestamp - last_keep_alive > 4:
                    last_keep_alive = timestamp
                    self.device.write(tmsi.Packet.construct( \
                        tmsi.PACKET_TYPE.TMS_KEEP_ALIVE).get_raw())
            except AssertionError, exception:
                if str(exception) == "Invalid checksum":
                    # silently ignore such samples
                    print "Received packet with wrong checksum"
                else:
                    raise exception
                

class RBuf:
    def __init__(self, f, n=0):
        self.f = f
        self.n = n
        self.buf = []
        self.cnt = 0
    
    def prepare(self, msg_type):
        ok = False
        while not ok:
            level = 0
            while level != 2:
                x = self.read(1)
                if x == "\xaa":
                    level += 1
                else:
                    level = 0
            head = self.read(2)
            size = ord(head[0])
            type = ord(head[1])
            m = self.read(size * 2 + 2)
            packet = "\xaa\xaa" + head + m
            sum = tmsi.calculate_checksum(packet)
            sum = tmsi.string_word_to_number(sum)
            if sum == 0 and type == msg_type:
                ok = True
                self.buf = packet
                self.cnt = len(packet)

    def read(self, cnt=-1):
        if cnt < 0:
            out = self.buf + self.f.recv(10**6)
            self.cnt = 0
            self.buf = []
        else:
            if cnt > self.cnt:
                rem = cnt + self.n - self.cnt
                while rem > 0:
                    dd = self.f.recv(rem)
                    rem -= len(dd)
                    self.buf += dd
            out = self.buf[:cnt]
            self.buf = self.buf[cnt:]
            self.cnt = len(self.buf)
        return "".join(out)

    def write(self, s):
        return self.f.send(s)

if __name__ == "__main__":
    gflags.DEFINE_bool('scan', False, 'Find some porti device to connect to')
    gflags.DEFINE_integer('duration', 8, 'How long scan should take')
    gflags.DEFINE_string("regex", "MobiMini", "Regex specifying TMSi device names")
    gflags.DEFINE_string("bt_addr", "", "Address of the amplifier we want to connect to")
    gflags.DEFINE_integer('port', 1, "Bluetooth port to use")
    gflags.DEFINE_integer("prefetch", 2048, "Number of bytes to be prefetched in reading")

    FLAGS = gflags.FLAGS
    try:
        argv = FLAGS(sys.argv)
    except gflags.FlagsError, e:
        print "%s\nUsage: %s ARGS\n%s" % (e, sys.argv[0], FLAGS)
        sys.exit(1)

    bt_addr = None
    bt_name = None
    if FLAGS.scan:
        print "Searching..."
        regexp = re.compile(FLAGS.regex)
        devs = bluetooth.discover_devices(duration=FLAGS.duration, lookup_names=True)
        for addr, name in devs:
            print 'Find', addr, name
            if regexp.search(name):
                print "Match!"
                bt_addr = addr
                bt_name = name
                break
        if not bt_addr:
            print "%s\n\nUsage: %s ARGS\n%s" % ("Cannot find any device matching " + FLAGS.regex, sys.argv[0], FLAGS)
            sys.exit(1)
    elif FLAGS.bt_addr:
        bt_addr = FLAGS.bt_addr
        bt_name = bluetooth.lookup_name(FLAGS.bt_addr)
    else:
        print "%s\n\nUsage: %s ARGS\n%s" % ("You should specify bt_addr or select scan", sys.argv[0], FLAGS)
        sys.exit(1)

    print "Connecting to", bt_addr, bt_name
    sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    sock.connect((bt_addr, FLAGS.port))

    TMSiBluetoothEEGAmplifier(RBuf(sock, 0)).start_amplifier().do_sampling()

