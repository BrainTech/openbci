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
from data_storage import signalml_read_manager

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
        self.signal_reader = signalml_read_manager.SignalmlReadManager(
            p_source_params['info_file'], 
            p_source_params['data_file'],
            p_source_params['tags_file'])
        self.signal_reader.start_reading()
        self.channel_numbers = self._get_channels_numbers()
        self.sampling_rate = self._get_sampling_rate()
        
        l_var = variables_pb2.Variable()
        l_var.key = "SamplingRate"
        l_var.value = str(self.sampling_rate)
        self.connection.send_message(message = l_var.SerializeToString(), 
                                     type = types.DICT_SET_MESSAGE, flush=True)

        l_var = variables_pb2.Variable()
        l_var.key = "AmplifierChannelsToRecord"
        l_var.value = ' '.join([str(num) for num in self.channel_numbers])
        self.connection.send_message(message = l_var.SerializeToString(), 
                                     type = types.DICT_SET_MESSAGE, flush=True)

    def _get_channels_numbers(self):
        """Return a collection of channel numbers (as ints) that are stored 
        in the file."""
        return [int(num) for num in self.signal_reader.get_param('channels_numbers')]

    def _get_sampling_rate(self):
        """Return sampling rate from info file."""
        return int(self.signal_reader.get_param('sampling_frequency'))

    def _get_sampling_start_time(self):
        """Return timestamp of first sample in file."""
        return float(self.signal_reader.get_param("first_sample_timestamp"))

    def do_sampling(self):
        """Fire super.sampling and tags sampling in separate thread."""
        thread.start_new_thread(self._do_tags_sampling, ())
        super(FileEEGAmplifier, self).do_sampling()

    def _do_tags_sampling(self):
        """Get tags from file and send `em to multiplexer in time."""
        l_old_start_time = self._get_sampling_start_time()
            
        l_real_start_time = time.time()
        while True:
            try:
                l_tag = self._get_next_tag()
            except signalml_read_manager.NoNextTag:
                LOGGER.info("End of tags file. Reding stopped.")
                break
            # Hmmm... lets look at the timeline
            # ---------------------|----------------------------|------
            #             l_real_start_time                 time.time()
            # l_real_passed_time = {                            }
            #
            #
            # ------------------|--------------------------------|----------
            #         l_old_start_time                 l_tag_start_timestamp
            # l_tag_wait_time = {                                }
            #
            # Let`s wait until l_tag_wait_time == l_real_passed_time
            l_real_passed_time = time.time() - l_real_start_time
            l_tag_wait_time = l_tag['start_timestamp'] - l_old_start_time
            l_to_sleep = l_tag_wait_time - l_real_passed_time
            if l_to_sleep > 0:
                time.sleep(l_to_sleep)
            TAGGER.send_unpacked_tag(l_tag)
        LOGGER.info("Finished sampling tags.")

    def _get_next_value(self, offset):
        """Return next value from the file. 
        Raise signalml_read_manager.NoNextValue exception if no tag is left."""
        return self.signal_reader.get_next_value()

    def _get_next_tag(self):
        """Return next tag from file. Raise signalml_read_manager.NoNextTag
        exception if no tag is left."""
        return self.signal_reader.get_next_tag()

        
        

