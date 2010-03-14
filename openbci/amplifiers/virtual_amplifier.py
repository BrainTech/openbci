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

import math
import time, variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client

class VirtualEEGAmplifier:
    def __init__(self, p_source="function", p_source_params={}):
        self.connection = connect_client(type = peers.AMPLIFIER)
        time.sleep(1)
        self._init_source_provider(p_source, p_source_params)
    def _init_source_provider(self, p_source, p_source_params):
        if p_source == "function":
            self.sampling_rate = int(self.connection.query(message="SamplingRate", type=types.DICT_GET_REQUEST_MESSAGE).message)
            self.channel_numbers = [int(x) for x in \
                                        self.connection.query(message="AmplifierChannelsToRecord", type=types.DICT_GET_REQUEST_MESSAGE).message.split(" ")]
            p_source_params['function'] = self.connection.query(message="VirtualAmplifierFunction", type=types.DICT_GET_REQUEST_MESSAGE).message
            self.source_provider = FunctionSourceProvider(p_source_params)
        elif p_source == "file":
            self.source_provider = FileSourceProvider(p_source_params)
            self.channel_numbers = [int(num) for num in self.source_provider.get_channel_names()]
            self.sampling_rate = int(self.source_provider.get_sampling_rate())

            l_var = variables_pb2.Variable()
            l_var.key = "SamplingRate"
            l_var.value = str(self.sampling_rate)
            self.connection.send_message(message = l_var.SerializeToString(), type = types.DICT_SET_MESSAGE, flush=True)

            l_var = variables_pb2.Variable()
            l_var.key = "AmplifierChannelsToRecord"
            l_var.value = ' '.join([str(num) for num in self.channel_numbers])
            self.connection.send_message(message = l_var.SerializeToString(), type = types.DICT_SET_MESSAGE, flush=True)



        #self.file = open("start_stream", 'w')
    def do_sampling(self):
        offset = 0
        start_time = time.time()
        while True:
            channels_data = []
            for channel_number in self.channel_numbers:
                channels_data.append(self.source_provider.get_next_value(offset))
            offset += 1
            sampleVector = variables_pb2.SampleVector()
            t = float(time.time())
            for x in channels_data:
                samp = sampleVector.samples.add()
                samp.value = float(x)
                samp.timestamp = float(t)
                #print "tstamp: ", samp.timestamp
                #print "val ",samp.value
            #for x in sampleVector.samples:
            #print "tstamp ", sampleVector.samples[0].timestamp
            #`print "val ", sampleVector.samples[0].value
            #if (offset <= 2):
            #    self.file.write(sampleVector.SerializeToString())
            #if (offset == 2):
            #    self.file.close()
#            channels_data_message = " ".join(str(x) for x in channels_data)
            # print sampleVector
            # print "break"

            self.connection.send_message(message=sampleVector.SerializeToString(), type=types.AMPLIFIER_SIGNAL_MESSAGE, flush=True)
            time_to_sleep = start_time + offset * (1. / self.sampling_rate) - time.time()
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)


from data_storage import signalml_read_manager
class FileSourceProvider(object):
    """The class provides subsequential signal data from a file in openbci format. Files path must be given in __init__ method."""
    def __init__(self, p_source_params):
        self._signal_reader = signalml_read_manager.SignalmlReadManager(p_source_params['info_file'], p_source_params['data_file'])
        self._signal_reader.start_reading()
    def get_next_value(self, offset):
        """Return next value from the file. Start reading from the begining if end-of-file."""
        try:
            return self._signal_reader.get_next_value()
        except signalml_read_manager.NoNextValue:
            self._signal_reader.start_reading()
            try:
                return self._signal_reader.get_next_value()
            except signalml_read_manager.NoNextValue:
                print("Data file is empty!")
                sys.exit(1)
                
    def get_channel_names(self):
        """Return a collection of channel numbers (as ints) that are stored in the file."""
        return [int(num) for num in self._signal_reader.get_param('channels_names')]

    def get_sampling_rate(self):
        """Return sampling rate from info file."""
        return self._signal_reader.get_param('sampling_frequency')
        
class FunctionSourceProvider(object):
    def __init__(self, p_source_params):
        self._function = p_source_params['function']
    def get_next_value(self, offset):
        return eval(self._function)
        
        

import sys
if __name__ == "__main__":
    """Run this script:
    1) without parameters or with function paramter to run amplifier from function (eg. python virtual_amplifier.py function)
    2) with file info_file data_file parameters to run amplifier from file 
    (eg. python virtual_amplifier.py file test.obci.info test.obci.dat)"""
    l_mode = 'function'
    l_info_file = './openbci/data_storage/sample_data/juhu_speller_full.obci.info'
    l_data_file = './openbci/data_storage/sample_data/juhu_speller_full.obci.dat'
    try:
        l_mode = sys.argv[1]
    except IndexError:
        pass
    if not (l_mode in ['function', 'file']):
        print("Unrecognised mode in first argument, default 'function' mode assumed.")
    
    if l_mode == 'function':
        print("Run VirtualAmplifier from function")
        VirtualEEGAmplifier().do_sampling()
    elif l_mode == 'file':
        try:
            l_info_file = sys.argv[2]
            l_data_file = sys.argv[3]
        except IndexError:
            print("No info and data files giver. Using data_storage/sample_data/juhu_speller_full*")
        print("Run VirtualAmplifier from '"+l_data_file+"' file.")
        VirtualEEGAmplifier('file', {'info_file':l_info_file, 'data_file':l_data_file}).do_sampling()


