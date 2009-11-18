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
Library to handle protocol used by TMSi EEG Amplifiers.
"""

__author__ = "kulewski@gmail.com (Krzysztof Kulewski)"

import math

WORD_SIZE = 2  #: word size in bytes

def number_to_string_word(number):
    """
    Convert a number 0..65535 to two byte string representation.
    First byte is less significant.
    
    @type number:   number
    @param number:  number to be converted.
    @rtype:         string
    @return:        two byte string containing representation of a word.
    """
    return chr(number % 256) + chr(number / 256)

def string_word_to_number(data):
    """
    Convert a two byte string representation of a number back into number.
    First byte is less significant.
    
    @type data:     string
    @param data:    two byte string containing representation of a word.
    @rtype:         number
    @return:        a number described by data parameter.
    """        
    assert len(data) == WORD_SIZE, "Word size invalid"
    return ord(data[1]) * 256 + ord(data[0])

def calculate_checksum(data):
    """
    Calculates checksum of a packet and return two byte (one word) string
    containing it.
    
    @type data:     string
    @param data:    data we want checksum of
    @rtype:         string (two byte) representing checksum
    @return:        checksum of data
    """
    word_sum = 0
    for i in range(len(data)):
        word_sum = (word_sum + ord(data[i]) * 256 ** (i % 2)) % 65536
    word_sum = (65536 - word_sum) % 65536
    return number_to_string_word(word_sum)

def num_to_bits(num):
    """
    Convert number into its binary representation (list of bits).
    Number has to be from 0..255 range.
    
    @type num:  number
    @param num: number to be converted into bit representation
    @rtype:     list of ints
    @return:    list of bits representing number num
    """
    bits = []
    for _ in range(8):
        bits.append(num % 2)
        num = num / 2
    return bits

def bits_to_num(bits):
    """
    Convert bit representation of a number (as large as you can imagine) back
    into number - int.
    
    @type bits:     list of ints
    @param bits:    binary representation of a number
    @rtype:         number
    @return:        number represented by a given list of bits
    """
    bits2 = bits[:]
    bits2.reverse()
    num = 0
    for bit in bits2:
        num = 2 * num + bit
    return num

class PacketType(object):
    """
    This class names all suported packet types.
    """
    
    TMS_ACKNOWLEDGE = 0x00
    TMS_CHANNEL_DATA = 0x01
    TMS_FRONTEND_INFO = 0x02
    TMS_FRONTEND_INFO_REQUEST = 0x03
    TMS_KEEP_ALIVE = 0x27
    TMS_VL_DELTA_DATA = 0x2f
    TMS_VL_DELTA_INFO_REQUEST = 0x30
    TMS_VL_DELTA_INFO = 0x31
    
    all_known_types = []  #: list of all known types, dynamically generated
    names = {}  #: dict of name => value, dynamically generated
    values = {}  #: dict of value => name, dynamically generated
    
    def generate_internals(self):
        """
        Generate internal fields: all_known_types, names, values
        """
        for key in dir(PacketType):
            value = self.__getattribute__(key)
            if isinstance(value, int):
                self.all_known_types.append(value)
                self.names[key] = value
                self.values[value] = key
    
    def print_types(self):
        """
        Show all available packet types.
        """
        print self.names
    
    def __init__(self):
        """
        Generates all_known_types, names, values.
        """
        super(PacketType, self).__init__()
        self.generate_internals()

PACKET_TYPE = PacketType()  # we want one instance of this class


class Header(object):
    """
    Header of data block. 
    Does not support packets longer than 254 words (such packets)
    have variable header length.
    
    TMSi protocol header is in format:
    - 2 start bytes: \xaa\xaa
    - length byte: number of words in packet
    - 1 byte: type of packet 
    """

    HEADER_SIZE = 4  #: size of a header in bytes
    HEADER_START = "\xaa\xaa"  #: magic string starting header
    MAX_PACKET_LENGTH = 254  #: maximal supported packet length
    TYPE_OFFSET = 3  #: byte offset in header of packet type indicator
    LENGTH_OFFSET = 2  #: byte offset in header of packet length indicator

    @classmethod
    def construct(cls, packet_type, length):
        """
        Construct packet header based on packet type and packet length.
        Set raw representation of header based on given parameters.
        Validate given packet type against list of all supported packet types.
        
        @type packet_type:  number (one of PACKET_TYPE constants)
        @param packet_type: type of a packet for which we are creating header
        @type length:       number
        @param length:      length of a packet (in bytes)
        @rtype:             Header
        @return:            new Header instance.
        """
        assert length % 2 == 0, "Length should be an even number"
        self = cls()
        self.packet_type = packet_type
        self.length = length
        assert self.packet_type in PACKET_TYPE.all_known_types, \
            "Invalid (or not supported) packet type"
        self.raw = self.HEADER_START + chr(length / 2) + chr(packet_type)
        return self
    
    @classmethod
    def read_one(cls, stream, search=False):
        """
        Reads one header from stream and returns new Header instance.
        If search options is present then search for header start in the stream
        by dropping "bad" characters.
        
        @type stream:   object with read(int) method (some file or stream)
        @param stream:  Stream containing header data.
        @type search:   bool
        @param search:  True iff bytes not starting header should be dropped
                        from the beginning of the stream.
        @rtype:         Header
        @return:        new Header instance.
        """
        self = cls()
        data = stream.read(4)
        if search:
            while data[:len(self.HEADER_START)] != self.HEADER_START:
                new_data = stream.read(1)
                assert len(new_data) == 1, "read(1) returned not 1 byte"
                data = data[1:] + new_data
        else:
            assert data[:len(self.HEADER_START)] == self.HEADER_START, \
                "Invalid packet start"
        assert len(data) == self.HEADER_SIZE, "Header of invalid size"
        self.packet_type = ord(data[self.TYPE_OFFSET])  # packet type
        assert self.packet_type in PACKET_TYPE.all_known_types, \
            "Invalid (or not supported) packet type"
        self.length = \
            WORD_SIZE * ord(data[self.LENGTH_OFFSET])  # decode packet length
        # we do not support data block longer than 254 words
        assert self.length <= WORD_SIZE * self.MAX_PACKET_LENGTH, \
            "Packet length exceeds max length"
        self.raw = data
        return self
    
    def __init__(self):
        object.__init__(self)
        self.packet_type = -1  # type of a packet, one defined in PACKET_TYPE
        self.length = -1  # packet length in bytes, not inc. header and checksum
        self.raw = ""  # raw binary value of header
    
    def __str__(self):
        return "TMSi Packet Header describing packet of type %s and length " \
            "of %d bytes." % (PACKET_TYPE.values[self.packet_type], self.length)


class Packet(object):
    """
    Wire packet base class.
    
    This class is the base of all packet classes. It provides common options
    related functionaility.
    
    TMSi protocol packet is in format:
    - 4 byte header: if packet is shorter than 254 words (other are unsupported)
    - packet data
    - 2 byte checksum
    """
    CHECKSUM_SIZE = 2  #: size of a checksum field

    @classmethod
    def construct(cls, packet_type, data=""):
        """
        Construct packet based on packet type and packet data.
        Calculate checksum of a packet.
        
        @type packet_type:  number (one of PACKET_TYPE constants)
        @param packet_type: type of a packet for which we are creating header
        @type data:         string
        @param length:      data inside a packet
        @rtype:             Packet
        @return:            new Packet instance.
        """
        self = cls()
        self.data = data
        self.header = Header.construct(packet_type, len(data))
        self.recalculate_checksum()
        return self

    @classmethod
    def read_one(cls, stream, search=False):
        """
        Reads one data packet from stream and returns Packet instance.
        
        @type stream:   object with read(int) method (some file or stream)
        @param stream:  Stream containing packet (including header and checksum)
        @type search:   bool
        @param search:  True iff bytes not starting header should be dropped
                        from the beginning of the stream.
        @rtype:         Packet
        @return:        new Packet instance.
        """
        self = cls()
        self.header = Header.read_one(stream, search)
        self.check_type()
        rest = stream.read(self.header.length + self.CHECKSUM_SIZE)
        self.checksum = rest[-self.CHECKSUM_SIZE:]
        self.data = rest[:-self.CHECKSUM_SIZE]
        assert calculate_checksum(self.header.raw + self.data) == \
            self.checksum, "Invalid checksum"
        return self

    def __init__(self):
        object.__init__(self)
        self.data = ""  # packet data
        self.header = None  # packet header
        self.checksum = ""  # packet checksum
        self.declared_type = None  # enforce some packet type in subclasses

    def get_word(self, index):
        """
        Get number represented by index-th word of packet.
        
        @type index:    number
        @param index:   index of word (in word-size units)
        @rtype:         number
        @return:        value represented by index-th word of packet
        """
        return string_word_to_number(self.data[index * WORD_SIZE: \
            index * WORD_SIZE + WORD_SIZE])
        
    def set_word(self, index, value):
        """
        Set a word in packet.
        
        @type index:    number
        @param index:   index of word (in word-size units)
        @type value:    number
        @param value:   value to be put into index-th word of packet
        """
        word = number_to_string_word(value)
        bits = list(self.data)
        bits[index * WORD_SIZE] = word[0]
        bits[index * WORD_SIZE + 1] = word[1]
        self.data = "".join(bits)

    def recalculate_checksum(self):
        """
        Updates checksum of a packet after some changes.
        """
        self.checksum = calculate_checksum(self.header.raw + self.data)

    def get_raw(self):
        """
        Get raw packet data.
        Serialize packet.
        
        @rtype:     string
        @return:    raw representation of packet (header, data, checksum)
        """
        return self.header.raw + self.data + self.checksum

    def check_type(self):
        """
        Check if packet has packet type coherent with declared packet type
        (if any).
        """
        if self.declared_type != None:
            assert self.header.packet_type == self.declared_type, \
                "Wrong packet type"
    
    def __str__(self):
        return "TMSi Packet of type %s with data length %s bytes [total " \
            "%d bytes]." % (PACKET_TYPE.values[self.header.packet_type], \
                self.header.length, 
                self.header.HEADER_SIZE + self.header.length + \
                    self.CHECKSUM_SIZE)


class Acknowledge(Packet):
    """
    Represents acknowledge packet.
    """
    
    ERRORS = {
        0x01: "unknown or not implemented blocktype",
        0x02: "CRC error in received block",
        0x03: "error in command data (can't do that)",
        0x04: "wrong blocksize (too large)",
        0x11: "No external power supplied",
        0x12: "Not possible because the Front is recording",
        0x13: "Storage medium is busy",
        0x14: "Flash memory not present",
        0x15: "nr of words to read from flash memory out of range",
        0x16: "flash memory is write protected",
        0x17: "incorrect value for initial inflation pressure",
        0x18: "wrong size or values in BP cycle list",
        0x19: "sample frequency divider out of range (<0, >max)",
        0x1A: "wrong nr of user channels (<=0, >maxUSRchan)",
        0x1B: "adress flash memory out of range",
        0x1C: "Erasing not possible because battery low",
    }
    
    def __init__(self):
        super(Acknowledge, self).__init__()
        self.declared_type = PACKET_TYPE.TMS_ACKNOWLEDGE
    
    def get_error_code(self):
        """
        Get error code.

        @rtype:     number
        @return:    error code
        """
        return self.get_word(1)
        
    def is_error(self):
        """
        Check if there is an error.
        Use get_error method to get error text.
        
        @rtype:     bool
        @return:    True iff there is an error"""
        return self.get_error_code() != 0
    
    def get_error(self):
        """
        @rtype:     string or None
        @return:    None if there is no error. Some error text (one from
                    values from ERROR dictionary) in the opposite case.
        """
        if self.is_error():
            return self.ERRORS.get(self.get_error_code(), "Unknown error")
        else:
            return None


class FrontendInfo(Packet):
    """
    Represents FrontendInfo packet.
    """
    BASE_SAMPLE_RATE_INDEX = 13
    NUMBER_OF_CHANNELS_INDEX = 12
    NUMBER_OF_HELP_CHANNELS = 2
    CURRENT_SAMPLE_RATE_INDEX = 1
    MODE_INDEX = 2
    MAX_DIVIDER = 4
    MODE_STREAM = 0
    MODE_STOP = 1
    
    def __init__(self):
        super(FrontendInfo, self).__init__()
        self.declared_type = PACKET_TYPE.TMS_FRONTEND_INFO
    
    def get_base_sample_rate(self):
        """
        Extract base sample rate frequency from FrontendInfo packet.
        
        @rtype:     number
        @return:    base sample frequency of amplifier
        """
        return self.get_word(self.BASE_SAMPLE_RATE_INDEX)
    
    def get_number_of_data_channels(self):
        """
        Extract number of channels from FrontendInfo packet.
        
        @rtype:     number
        @return:    number of hardware channels in amplifier
        """
        return self.get_word(self.NUMBER_OF_CHANNELS_INDEX) - \
            self.NUMBER_OF_HELP_CHANNELS
    
    def modify_sample_rate(self, frequency):
        """
        Set sample frequency in (obtained from device) FrontendInfo packet.
        
        @type frequency:    number
        @param frequency:   frequency to be set to
        """
        base = self.get_base_sample_rate()
        divider = math.log(base / frequency, 2)
        assert divider == int(divider), "Frequency must be a power of two"
        divider = int(divider)
        assert divider in range(self.MAX_DIVIDER + 1), "Unsupported frequency"
        self.set_word(self.CURRENT_SAMPLE_RATE_INDEX, divider)
    
    def start(self):
        """
        Modify FrontendInfo packet to enable data streaming.
        """
        self.set_word(self.MODE_INDEX, self.MODE_STREAM)
    
    def stop(self):
        """
        Modify FrontendInfo packet to disable streaming.
        """
        self.set_word(self.MODE_INDEX, self.MODE_STOP)


class ChannelData(Packet):
    """
    Packet containing channel data NOT encoded using VL Delta compression.
    """
    OVERFLOW = 2 ** 23
    ON_OFF_BUTTON = 0x01
    TRIGGER_ACTIVE = 0x04
    BATTERY_LOW = 0x40

    def __init__(self):
        super(ChannelData, self).__init__()
        self.declared_type = PACKET_TYPE.TMS_CHANNEL_DATA
        self.number_of_channels = -1

    def set_number_of_channels(self, number_of_channels):
        """
        Set number of channels (obtainted from FrontendInfo).
        
        @type number_of_channels:   number
        @param number_of_channels:  number of channels (from FrontendInfo)
        """
        self.number_of_channels = number_of_channels

    def extract_channel_data(self, channel_number):
        """
        Extract data of single channel.
        
        @type channel_number:   number
        @param channel_number:  number of channel we want to extract data from
        @rtype:                 number
        @return:                value of channel_number-th channel data
        """
        return ord(self.data[3 * channel_number]) + \
               ord(self.data[1 + 3 * channel_number]) * 256 + \
               ord(self.data[2 + 3 * channel_number]) * 65536 - \
               (2 ** 24 if ord(self.data[2 + 3 * channel_number]) > 128 else 0)

    def get_digi(self):
        """
        Get Digi channel status.
        This channel contains data such as battery level, on off button status,
        trigger status.
        
        @rtype:     number
        @return:    byte containing flags (on/off button etc.) set in packet
        """
        return ord(self.data[3 * self.number_of_channels])

    def check_digi(self, condition):
        """
        Check if flag condition is set in digi channel.
        
        @type condition:    number
        @param condition:   Bit flag representing some state. Valid flags are:
                            ON_OFF_BUTTON, TRIGGER_ACTIVE, BATTERY_LOW.
        @rtype:             bool
        @return:            True iff condition is set in digi channel.
        """
        return self.get_digi() & condition == condition

    def on_off_pressed(self):
        """
        Check if on/off button is pressed.
        
        @rtype:     bool
        @return:    True iff on/off button is pressed.
        """
        return self.check_digi(self.ON_OFF_BUTTON)
    
    def trigger_active(self):
        """
        Check if trigger is active.
        
        @rtype:     bool
        @return:    True iff trigger is active.
        """
        return self.check_digi(self.TRIGGER_ACTIVE)
    
    def battery_low(self):
        """
        Check if battery is low.
        
        @rtype:     bool
        @return:    True iff battery is low.
        """
        return self.check_digi(self.BATTERY_LOW)
    
    def decode(self):
        """
        Decode channel data contained in this packet.
        
        @rtype:     list of lists of ints
        @return:    List indexed by channel numbers. Every list contains
                    list of values in this channel.
        """
        return [[self.extract_channel_data(x)] for x in \
            range(self.number_of_channels)]


class VLDeltaInfo(Packet):
    """
    Packet containing VL Delta information (like transmission frequency
    divider).
    """
    
    def __init__(self):
        super(VLDeltaInfo, self).__init__()
        self.declared_type = PACKET_TYPE.TMS_VL_DELTA_INFO
    
    def get_trans_freq_div(self):
        """
        Returns value of transmission frequency divider from current packet.
        
        @rtype:     number
        @return:    transmission frequency divider
        """
        return self.get_word(2)
    
    def get_divider_list(self, number_of_channels):
        """
        Decode dividers list from tha packet.
        
        @type number_of_channels:   number
        @param number_of_channels:  number of data channels (not including digi
                                    and saw channels)
        @rtype:                     list of ints
        @return:                    list of all dividers (including digi
                                    and saw channels)
        """
        return [2 ** self.get_word(3 + a) for a in \
            range(number_of_channels + FrontendInfo.NUMBER_OF_HELP_CHANNELS)]


class VLDeltaData(ChannelData):
    """
    Packet containing VL Delta channel data.
    Supports VL Delta compression.
    
    Delta dat packet has the following format:
    - header
    - references: data in all channels at the beginning of quant of time,
        including data for digi and saw channels, these values are encoded like
        in normal ChannelData packet
    - delta bits: see below
    - filling (because delta bits len can not be divisible by 16bit = word size)
    - checksum
    
    Delta bits is raw stream of bits.
    Every delta is encoded as 4 bit length + delta body.
    Delta length can name values from 0 to 15. If length is 0, then delta body
    has 2 bits! In opposit case, delta body has delta length bits.
    Delta length 0 (so in length we have all 0bits: "0000" bits) is used to 
    encode special delta values:
    - 0 - delta = 0
    - 1 - this value is never used!
    - 2 - channels is in overflow
    - 3 - delta = -1
    
    Every channel can have different divider. Lets consider an example, where
    there are only two channels: A and B.
    Channel A is send with 128Hz freq.
    Channel B is send with 256Hz freq.
    Base frequency is set to 64Hz.
    Then in 1/64s we have 2 data in A and 4 data in B.
    So the VLDelta packet will consist of reference samples: 1 for A and
    1 for B. Then it will multiplex:
    delta for channel B, delta for channel A, delta for channel B, delta for
    channel B.
    If some channel was in overflow at the beginning of quant of time then
    it is not included later in deltas (till the end of this packet).
    If some channel become in overflow in the middle of the packet,
    this is signalised by using special delta, and later this channel will
    not be send in deltas (till the end of this packet).
    """
    
    def __init__(self):
        super(VLDeltaData, self).__init__()
        self.declared_type = PACKET_TYPE.TMS_VL_DELTA_DATA
        self.channel_data = []
        self.vldelta_info = None
        self.delta_bits = None
    
    def set_vldelta_info(self, vldelta_info):
        """
        Set VLDelta Info (user should obtain one from device before calling
        decode method).
        
        @type vldelta_info:     VLDeltaInfo
        @param vldelta_info:    packet of type vldelta info containing divider
                                list
        """
        self.vldelta_info = vldelta_info

    def decode_next_delta(self):
        """
        Decode one delta data from delta_bits attribute.
        Later delete decoded data from delta_bits.
        
        @rtype:     tuple (bool, int)
        @return:    (was this delta special, value of delta)
        """
        assert len(self.delta_bits) > 4, "Not enough bits to decode delta len"
        delta_len = original_delta_len = \
            bits_to_num(self.delta_bits[:4])
        if delta_len == 0:
            delta_len = 2
        assert len(self.delta_bits) >= 4 + delta_len, \
            "Not enough bits to decode delta body"
        delta = bits_to_num(self.delta_bits[4:4 + delta_len])
        special = original_delta_len == 0
        if not special:
            if self.delta_bits[4 + delta_len - 1] == 0:
                delta = -delta
        self.delta_bits = self.delta_bits[4 + delta_len:]
        return (special, delta)

    def decode(self):
        """
        Decode channel data contained in this packet.
        Supports VL Delta compression.
        
        @rtype:     list of lists of ints
        @return:    List indexed by channel numbers. Every list contains
                    list of values in this channel.
        """
        divider_list = self.vldelta_info.get_divider_list( \
            self.number_of_channels)
        assert len(divider_list) == \
            self.number_of_channels + FrontendInfo.NUMBER_OF_HELP_CHANNELS, \
            "Divider list of invalid length"
        
        self.channel_data = [[self.extract_channel_data(x)] for x in \
            range(self.number_of_channels)]
        self.channel_data += [[ord(self.data[3 * self.number_of_channels])], \
            [ord(self.data[1 + 3 * self.number_of_channels])]]
        overflow = [x == [self.OVERFLOW] for x in self.channel_data]
        
        self.delta_bits = reduce(lambda x, y: x + y, \
            (num_to_bits(ord(x)) for x in \
                self.data[3 * self.number_of_channels + \
                    FrontendInfo.NUMBER_OF_HELP_CHANNELS:]))
        for i in range(1, self.vldelta_info.get_trans_freq_div() + 1):
            for j in range(self.number_of_channels + \
                FrontendInfo.NUMBER_OF_HELP_CHANNELS):
                if i % divider_list[j] == 0:
                    if not overflow[j]:
                        special, delta = self.decode_next_delta()
                        if special:
                            if delta == 0:
                                self.channel_data[j].append( \
                                    self.channel_data[j][-1])
                            elif delta == 1:
                                assert False, "Special delta 1 not used"
                            elif delta == 2:
                                overflow[j] = True
                                self.channel_data[j].append(self.OVERFLOW)  
                            elif delta == 3:
                                self.channel_data[j].append( \
                                    self.channel_data[j][-1] - 1)
                        else:
                            self.channel_data[j].append( \
                                self.channel_data[j][-1] + delta)
                    else:
                        self.channel_data[j].append(self.OVERFLOW)

        return self.channel_data[:-FrontendInfo.NUMBER_OF_HELP_CHANNELS]

    def get_digi(self):
        """
        Get Digi channel status.
        This channel contains data such as battery level, on off button status,
        trigger status.
        
        For VLDelta Data packet, which can contain multiple information
        in digi channel, this is done by taking binary alternative of all
        digi channel values.
        
        @rtype:     number
        @return:    byte containing flags (on/off button etc.) set in packet
        """
        return reduce(lambda x, y: x | y, \
            self.channel_data[self.number_of_channels])



def __test():
    """
    Test functionality of this module by:
    - interpreting one Frontend Info Packet
    - interpreting one VLDelta Info Packet
    - interpreting and decoding one VLDelta Data Packet using previous packets
    """
    import StringIO
    
    bad_acknowledge_str = "\xaa\xaa\x02\x00\x10\x02\x19\x00\x2b\x53"

    frontend_info_str = \
'\xaa\xaa\x10\x02"\x00\x03\x00\x01\x00\x00\x02X\xf1W\x0c\x18'\
'\x00\x08\x00 \x07%\x07\x8c\x00\x8a\x00"\x00\x00\x08\xff\xff\xff\xff\xd6;'

    vldelta_info_str = \
'\xaa\xaa%1\x00\x00\x04\x00\x07\x00\x01\x00\x01\x00\x01\x00\x01'\
'\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00'\
'\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00\x01'\
'\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x03\x00\x03\x00\x03\x00'\
'\x00\x00\x00\x00\x02$'

    vldelta_data_str = \
'\xaa\xaaI/\xdfo\x01\xde\xbe\x01\x98\xd4\xfd\x00\x00\x80\xbe^'\
'\x01\x05y\x03\x00\x00\x80\x00\x00\x80\x00\x00\x80\x00\x00\x80\x00\x00\x80\x00'\
'\x00\x80\x00\x00\x80\x00\x00\x80\x00\x00\x80\x00\x00\x80\x00\x00\x80\x00\x00'\
'\x80\x00\x00\x80\x00\x00\x80\x00\x00\x80\x00\x00\x80\x00\x00\x80\x00\x00\x80'\
'\x00\x00\x80\x00\x00\x80\x00\x00\x80\x00\x00\x80\x00\x00\x80\x00\x00\x80\x00'\
'\x00\x80\x00\x00\x80\x021\x80\xf8\x01\x80\x0f\x00|\x00\xe0\x03\x00\x1f\x00'\
'\x00D@\xfc\x00\xc0\x07\x00>\x00\xf0\x01\x80\x0f\x00\x00" ~\x00\xe0\x03\x00'\
'\x1f\x00\xf8\x00\xc0\x97*\x00\x11\x10\x01\xaf\xee\xf6'
    
    decode_result = [[94175, 94174, 94173, 94172], \
        [114398, 114397, 114396, 114395], \
        [-142184, -142185, -142186, -142187], \
        [8388608, 8388608, 8388608, 8388608], \
        [89790, 89789, 89788, 89787], \
        [227589, 227588, 227587, 224862], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608], \
        [8388608, 8388608, 8388608, 8388608, 8388608, 8388608, 8388608, \
            8388608], \
        [8388608, 8388608, 8388608, 8388608, 8388608, 8388608, 8388608, \
            8388608], \
        [8388608, 8388608, 8388608, 8388608, 8388608, 8388608, 8388608, \
            8388608], \
        [8388608, 8388608, 8388608, 8388608, 8388608, 8388608, 8388608, \
            8388608], \
        [8388608], [8388608], [8388608], [8388608]]
    digi_status_result = [False, False, False]
    acknowledge_result = [True, \
        "sample frequency divider out of range (<0, >max)", 25]

    # Test Acknowledge packet
    acknowledge_packet = Acknowledge.read_one(StringIO.StringIO( \
        bad_acknowledge_str))
        
    assert [acknowledge_packet.is_error(), acknowledge_packet.get_error(), \
        acknowledge_packet.get_error_code()] == acknowledge_result, \
        "Acknowledge packet decoding error"

    # Test FrontendInfo packet
    frontend_info_packet = FrontendInfo.read_one( \
        StringIO.StringIO(frontend_info_str))
    
    # Test VLDeltaInfo packet
    vldelta_info_packet = VLDeltaInfo.read_one( \
        StringIO.StringIO(vldelta_info_str))
    
    # Test VLDeltaData packet
    vldelta_data_packet = VLDeltaData.read_one( \
        StringIO.StringIO(vldelta_data_str))
    vldelta_data_packet.set_number_of_channels( \
        frontend_info_packet.get_number_of_data_channels())
    vldelta_data_packet.set_vldelta_info(vldelta_info_packet)
    
    # Test VLDeltaData packet decode
    assert vldelta_data_packet.decode() == decode_result, "VLDelta decode error"
    # Test VLDeltaData trigget check
    assert [vldelta_data_packet.trigger_active(), \
        vldelta_data_packet.battery_low(), \
        vldelta_data_packet.on_off_pressed()] == digi_status_result, \
            "Digi status decode error"
    print "Test: OK"

if __name__ == "__main__":
    __test()

        