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
data_file_extension = ".obci.dat"
info_file_extension = ".obci.info"
tags_file_extension = ".obci.tags"
timestamps_file_extension = ".obci.timestamps"


class SignalmlSaveManager(object):
    """A class that is responsible for implementing logics of openbci signal stroing
    eg. what goes to which files, what kind of files are to be created etc.
    The class should be separated from all multiplexer-stuff logics.
    SaverObject represents a process of saving one signal.
    Public interface:
    - finish_saving()
    - data_received(p_data_sample)
    """
    def __init__(self, p_session_name, p_dir_path, p_signal_params):
        """
        Init data file and info file proxies representing saving process.
        Arguments:
        p_session_name - a name of file(s) to be created
        p_dir_path - a path to dir where files are to be created
        p_signal_params- a dictionary of signal parameters like number of channels etc, 
        params should be readablye by InfoFileProxy, see its __init__ method t learn more.
        """
        self._info_proxy = info_file_proxy.InfoFileWriteProxy(
            p_session_name, p_dir_path, p_signal_params, info_file_extension)
        self._data_proxy = data_file_proxy.DataFileWriteProxy(
            p_session_name, p_dir_path, data_file_extension)
        self._tags_proxy = tags_file_writer.TagsFileWriter(
            p_session_name, p_dir_path, tags_file_extension)
        self._timestamps_proxy = data_file_proxy.AsciFileWriteProxy(
            p_session_name, p_dir_path, timestamps_file_extension)
        self._first_sample_timestamp = -1.0

    def finish_saving(self):
        """ Return a tuple x,y where:
        x - canonised path to info file
        y - canonised path to data file
        """
        #TODO - sprawdzanie bledow
        l_data_file_path, l_samples_count = self._data_proxy.finish_saving()
        self._info_proxy.set_attributes({
                'number_of_samples': l_samples_count,
                'first_sample_timestamp': self._first_sample_timestamp,
                'file': os.path.basename(l_data_file_path)})
                                        
        l_info_file_path = self._info_proxy.finish_saving()
        l_tags_file_path = self._tags_proxy.finish_saving()
        l_timestamps_file_path = self._timestamps_proxy.finish_saving()
        return l_info_file_path, l_data_file_path, l_tags_file_path, l_timestamps_file_path


    def data_received(self, p_data, p_timestamp):
        """Validate p_data (is it a correct float? If not exit the program.), send it to data_proxy."""
        try:
            self._data_proxy.data_received(p_data)
        except data_storage_exceptions.BadSampleFormat, e:
            LOGGER.error("Received sample is not of a good size. Writing aborted!")
            sys.exit(1)
        self._timestamps_proxy.data_received(p_timestamp)
        if self._first_sample_timestamp < 0:#TODO - zrobic, zeby za kazdym razem to sie nie sprawdzalo
            self._first_sample_timestamp = p_timestamp

    def tag_received(self, p_tag_dict):
        self._tags_proxy.tag_received(p_tag_dict)

            
