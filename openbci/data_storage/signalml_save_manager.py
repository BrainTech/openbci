# -*- coding: utf-8 -*-
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
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

import sys
import os.path
import info_file_proxy
import data_file_proxy
from openbci.tags import tags_file_writer
import data_storage_exceptions
import data_storage_logging as logger
LOGGER = logger.get_logger("signalml_save_manager", 'info')

data_file_extension = ".obci.dat"
info_file_extension = ".obci.info"
svarog_info_file_extension = ".obci.svarog.info"
tags_file_extension = ".obci.tags"
svarog_tags_file_extension = ".obci.svarog.tags"
timestamps_file_extension = ".obci.timestamps"


USE_SVAROG_INFO_PROXY = True
USE_TIMESTAMPS = False
"""set to true if we want to have two info proxies saved - our`s, obci cool proxy, and svarog`s dirty proxy."""

class SignalmlSaveManager(object):
    """A class that is responsible for implementing logics of openbci signal stroing
    eg. what goes to which files, what kind of files are to be created etc.
    The class should be separated from all multiplexer-stuff logics.
    SaverObject represents a process of saving one signal.
    Public interface:
    - finish_saving()
    - data_received(p_data_sample)
    """
    def _all_but_first_data_received(self, p_data, p_timestamp):
        """Validate p_data (is it a correct float? If not exit the program.), send it to data_proxy.
        _all_but_first_data_received is set to self.data_received in 
        self._first_sample_data_received, so in fact _all_but_first_data_received
        is fired externally by calling self.data_received."""

        try:
            self._data_proxy.data_received(p_data)
        except data_storage_exceptions.BadSampleFormat, e:
            LOGGER.error("Received sample is not of a good size. Writing aborted!")
            sys.exit(1)

    def _all_but_first_data_received_with_timestamp(self, p_data, p_timestamp):
        """Validate p_data (is it a correct float? If not exit the program.), send it to data_proxy.
        _all_but_first_data_received_with_timestamp is set to self.data_received in 
        self._first_sample_data_received, so in fact _all_but_first_data_received_with_timestamp
        is fired externally by calling self.data_received."""

        self._all_but_first_data_received(p_data, p_timestamp)
        self._timestamps_proxy.data_received(p_timestamp)

    def _first_sample_data_received(self, p_data, p_timestamp):
        """Validate p_data (is it a correct float? If not exit the program.), send it to data_proxy.
        first_sample_data_received is set to self.data_received in self.__init__, so in fact
        first_sample_data_received is fired externally by calling self.data_received"""

        # 
        if USE_TIMESTAMPS:
            self.data_received = self._all_but_first_data_received_with_timestamp
        else:
            self.data_received = self._all_but_first_data_received

        self.data_received(p_data, p_timestamp)

        # Set some additional first_sample-like data
        self._first_sample_timestamp = p_timestamp
        if USE_SVAROG_INFO_PROXY:
            self._svarog_tags_proxy.set_first_sample_timestamp(p_timestamp)
            


    def __init__(self, p_session_name, p_dir_path, p_signal_params):
        """
        Init data file and info file proxies representing saving process.
        Arguments:
        p_session_name - a name of file(s) to be created
        p_dir_path - a path to dir where files are to be created
        p_signal_params- a dictionary of signal parameters like number of channels etc, 
        params should be readablye by InfoFileProxy, see its __init__ method t learn more.
        """

        # Init info proxies - files for storing metadata
        self._info_proxies = []
        self._info_proxies.append(info_file_proxy.InfoFileWriteProxy(
            p_session_name, p_dir_path, 
            p_signal_params, info_file_extension))

        if USE_SVAROG_INFO_PROXY:
            import svarog_file_proxy
            self._info_proxies.append(
                svarog_file_proxy.SvarogFileWriteProxy(
                    p_session_name, p_dir_path, 
                    p_signal_params, svarog_info_file_extension)
                )

            from openbci.tags import svarog_tags_file_writer as wr
            self._svarog_tags_proxy = wr.SvarogTagsFileWriter(
            p_session_name, p_dir_path, svarog_tags_file_extension,
            p_signal_params['sampling_frequency'], p_signal_params['number_of_channels'])
                
        # Init standard: data and tags proxy
        self._data_proxy = data_file_proxy.DataFileWriteProxy(
            p_session_name, p_dir_path, data_file_extension)
        self._tags_proxy = tags_file_writer.TagsFileWriter(
            p_session_name, p_dir_path, tags_file_extension)


        if USE_TIMESTAMPS:
            # Init additional proxy
            self._timestamps_proxy = data_file_proxy.AsciFileWriteProxy(
                p_session_name, p_dir_path, timestamps_file_extension)

        # As we want to tread first sample individually we need to jungle with
        # self.data_received function - see self.first_sample_data_received
        # The reason is efficency, we don`t want any extra 'if' in self.data_received
        # as the function is being called very often
        self._first_sample_timestamp = -1.0
        self.data_received = self._first_sample_data_received

    def finish_saving(self):
        """ Return a tuple x,y where:
        x - canonised path to info file
        y - canonised path to data file
        """
        #TODO - sprawdzanie bledow
        l_data_file_path, l_samples_count = self._data_proxy.finish_saving()
        l_info_files_paths = []
        for i_proxy in self._info_proxies:
            i_proxy.set_attributes({
                    'number_of_samples': l_samples_count,
                    'first_sample_timestamp': self._first_sample_timestamp,
                    'file': os.path.basename(l_data_file_path)})
            l_info_files_paths.append(i_proxy.finish_saving())
        l_tags_file_path = self._tags_proxy.finish_saving()
        if USE_SVAROG_INFO_PROXY:
            self._svarog_tags_proxy.finish_saving()

        l_saved_files = [l_info_files_paths[0], l_data_file_path, 
                         l_tags_file_path, l_info_files_paths[1:]]
        if USE_TIMESTAMPS:
            l_timestamps_file_path = self._timestamps_proxy.finish_saving()
            l_saved_files.append(l_timestamps_file_path)
            
        return tuple(l_saved_files)


    def tag_received(self, p_tag_dict):
        self._tags_proxy.tag_received(p_tag_dict)
        if USE_SVAROG_INFO_PROXY:
            if self._first_sample_timestamp < 0:
                LOGGER.error("Can't save tag to svarog_tags_proxy as no sample hasn`t been received yet and we don`t have first_sample_timestamp")
            else:
                self._svarog_tags_proxy.tag_received(p_tag_dict)

            
