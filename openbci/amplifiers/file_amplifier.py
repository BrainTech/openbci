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
#      Mateusz Kruszynski <mateusz.kruszynski@gmail.com>
#

import math
import thread
import time
import variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client


import virtual_eeg_amplifier
import amplifiers_logging as logger
from openbci.tags import tagger
from openbci.data_storage import read_manager
from openbci.data_storage import data_storage_exceptions


LOGGER = logger.get_logger("file_amplifier")
TAGGER = tagger.get_tagger()

class FileEEGAmplifier(virtual_eeg_amplifier.VirtualEEGAmplifier):
    """A subclass of VirtualEEGAmplifier. Redefines initialisation and
    method get_next_value that returns next sample value.
    Values are taken from file.
    Its only public method is do_sampling(), not needed to redefine here."""

    def __init__(self, p_source_params):
        """Init all needed attributes:
        - self.sampling_rate
        - self.channel_numbers
        - self.signal_reader
        What`s more, send some data to hash table: SamplingRate, 
        AmplifierChannelsToRecord ...
        """
        super(FileEEGAmplifier, self).__init__()
        LOGGER.info("Run virtualamplifier from file: "+
                    str(p_source_params))
        self.signal_reader = read_manager.ReadManager(
            p_source_params['info_file'], 
            p_source_params['data_file'],
            p_source_params['tags_file'])
        self.tags_iter = self.signal_reader.iter_tags()
        self.signal_iter = self.signal_reader.iter_samples()

        self.sampling_rate = self._get_sampling_rate()
        self.num_of_channels = int(self.signal_reader.get_param('number_of_channels'))

        
        self._set_hashtable_value("SamplingRate", str(self.sampling_rate))
        self._set_hashtable_value("AmplifierChannelsToRecord",
                                  ' '.join([str(num) for num in range(self.num_of_channels)]))
        self._set_hashtable_value("Gain", ' '.join(self.signal_reader.get_param('channels_gains')))
        self._set_hashtable_value("Offset", ' '.join(self.signal_reader.get_param('channels_offsets')))
        self._set_hashtable_value("ChannelsNames", ';'.join(self.signal_reader.get_param('channels_names')))
        self._set_hashtable_value("NumOfChannels", self.signal_reader.get_param('number_of_channels'))

        #let other modules synchro with data
        time.sleep(10)


    def _set_hashtable_value(self, key, value):
        l_var = variables_pb2.Variable()
        l_var.key = key
        l_var.value = value
        self.connection.send_message(message = l_var.SerializeToString(), 
                                     type = types.DICT_SET_MESSAGE, flush=True)

    def _get_sampling_rate(self):
        """Return sampling rate from info file."""
        return int(self.signal_reader.get_param('sampling_frequency'))

    def do_sampling(self):
        """Fire super.sampling and tags sampling in separate thread."""
        thread.start_new_thread(self._do_tags_sampling, ())
        super(FileEEGAmplifier, self).do_sampling()

    def _do_tags_sampling(self):
        """Get tags from file and send `em to multiplexer in time."""

        l_real_start_time = time.time()
        while True:
            l_tag = self._get_next_tag()
            if not l_tag:
                LOGGER.info("End of tags file. Reding stopped.")
                break

            l_real_tag_time = l_real_start_time + l_tag['start_timestamp']
            l_tag['start_timestamp'] = l_real_tag_time
            l_tag['end_timestamp'] = l_real_start_time + l_tag['end_timestamp']

            l_to_sleep = l_real_tag_time - time.time()
            if l_to_sleep > 0:
                time.sleep(l_to_sleep)
            TAGGER.send_unpacked_tag(l_tag)
        LOGGER.info("Finished sampling tags.")

    def _get_next_sample(self, offset):
        """Return next value from the file. 
        Raise signalml_read_manager.NoNextValue exception if no tag is left."""
        try:
            return self.signal_iter.next()
        except StopIteration:
            return None

    def _get_next_tag(self):
        """Return next tag from file. Raise signalml_read_manager.NoNextTag
        exception if no tag is left."""
        try:
            return self.tags_iter.next()
        except StopIteration:
            return None


        
        

