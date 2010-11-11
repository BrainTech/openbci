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
import sys, struct, time, numpy
import xml.dom.minidom
from openbci.tags import tags_file_reader
from openbci.data_storage import data_storage_exceptions
import info_file_proxy
import data_file_proxy
import data_storage_logging as logger
LOGGER = logger.get_logger("signalml_read_manager", "info")

data_file_extension = ".obci.dat"
info_file_extension = ".obci.info"
tags_file_extension = ".obci.tags"
class DataFileManager(object):
    """A manager of signal data.
    Reads data from file, casches data in a two-dimentional array."""
    def __init__(self, p_data_file):
        """Only open the p_data_file file and init some internal structures."""
        self._data_reader = data_file_proxy.DataFileReadProxy(p_data_file)
        self._all_channeled_values = None
        self._sample_i = 0
        self._channel_i = 0

        self._ch_no = None

    def start_reading(self, p_ch_no):
        """Reload the file. p_ch_no is a number of channels in file."""
        self._all_channeled_values = None
        self._ch_no = p_ch_no
        self._sample_i = 0
        self._channel_i = 0
        self._data_reader.start_reading()

    def goto_value(self, p_value_no):
        """Set value pointer to p_value_no value."""
        if not self._all_channeled_values is None:
            # Set indexes if we have data cached
            self._sample_i = p_value_no / self._ch_no
            self._channel_i = p_value_no % self._ch_no

        else:
            # Set file pointer if we don`t have data cached
            self._data_reader.goto_value(p_value_no)
        
    def get_next_value(self):
        """Return next value."""
        if not self._all_channeled_values is None:
            # From cached data
            try:
                ret = self._all_channeled_values[self._channel_i][self._sample_i]
                self._channel_i = self._channel_i + 1
                return ret
            except IndexError:
                # Last channel is red or end of samples data
                self._sample_i = self._sample_i + 1
                self._channel_i = 0
                try:
                    ret = self._all_channeled_values[self._channel_i][self._sample_i]
                    self._channel_i = self._channel_i + 1
                    return ret
                except IndexError:
                    # End of data
                    raise data_storage_exceptions.NoNextValue()

        else:
            # Straight fro file
            return self._data_reader.get_next_value()

    def get_all_values(self, p_reload=False):
        """Return all values from data file (as a collection of 
        python floats)."""
        # Set file`s pointer to the beginning of the file
        LOGGER.info('Start getting all values')
        t = time.time()
        l_ch_values = self.get_all_channeled_values(p_reload)
        ret = []
        sample_i = 0
        ch_i = 0
        for i in range(len(l_ch_values[len(l_ch_values)-1])):
            for j in range(self._ch_no):
                ret.append(l_ch_values[j][i])
        LOGGER.info('end getting all values in time: '+str(time.time()-t))
        return ret

    def get_all_channeled_values(self, p_reload=False):
        """Return an two-dimentional array of values from the signal."""

        if not p_reload and not (self._all_channeled_values is None):
            return self._all_channeled_values
        self.start_reading(self._ch_no)
        self.goto_value(0)
        LOGGER.info('Start getting all channeled values')
        t = time.time()
        data = [[] for i in range(self._ch_no)]
        i_ch_num = 0
        while True:
            try:
                data[i_ch_num].append(self.get_next_value())
                i_ch_num = (i_ch_num + 1) % self._ch_no
            except data_storage_exceptions.NoNextValue:
                break
        LOGGER.debug('end getting all channeled values in time: '+str(time.time()-t))
        self._all_channeled_values = numpy.array(data)
        return self._all_channeled_values

    def set_all_channeled_values(self, p_data):
        """Set cached signal data to p_data."""
        self._all_channeled_values = numpy.array(p_data)
        self.goto_value(0)


        

class SignalmlReadManager(object):
    """A class responsible for reding openbci file format.
    Public interface:
    - start_reading() - open info and data file,
    - get_next_value() - get next value from data file,
    - get_param(param_name) - get param_name parameter from info file.

    Wanna be able to read a new parameter 'new_param'?
    1. Register reading function in self._create_info_tags_control() under 'new_param' key.
    2. Implement the function (it should be considered as class private function, not callable from outside; 
    the function should return a value for 'new_param' request).
    3. Call get_param('new_param') every time you want to get the param.
    """
    def __init__(self, p_info_file, p_data_file, p_tags_file=""):
        """Just remember info file path and data file path."""
        self._info_reader = info_file_proxy.InfoFileReadProxy(p_info_file)
        self._data_mgr = DataFileManager(p_data_file)


        if len(p_tags_file) == 0:
            self._tags_reader = None            
        else:
            self._tags_reader = tags_file_reader.TagsFileReader(p_tags_file)

    def start_reading(self):
        """Open info file, parse it and remember xml structure. 
        Open data file."""
        LOGGER.info("Try reading info and data file ...")
        self._info_reader.start_reading()
        self._data_mgr.start_reading(int(self.get_param('number_of_channels')))
        if self._tags_reader:
            self._tags_reader.start_tags_reading()
                
    def get_next_value(self):
        """Return next value from data file (as python float). 
        Close data file and raise NoNextValue exception if eof."""
        return self._data_mgr.get_next_value()

    def get_all_values(self):
        """Return all values from data file (as a collection of 
        python floats)."""
        return self._data_mgr.get_all_values(self)

    def get_all_channeled_values(self, p_reload=False):
        """Return a two dimensional array of signal values.
        if p_reload then refresh the file, otherwise use cached values."""
        return self._data_mgr.get_all_channeled_values(p_reload)

    def get_channel_values(self, p_ch_name):
        """Return an array of values for channel p_ch_name, or
        raise ValueError exception if there is channel with that name."""
        ch_ind = self.get_param('channels_names').index(p_ch_name)
        return self.get_all_channeled_values()[ch_ind]

        

    def set_all_channeled_values(self, p_values):
        self._data_mgr.set_all_channeled_values(p_values)

    def goto_value(self, p_value_no):
        """Set the reader engine, so that nex 'get_next_value' call will return
        value number p_value_no+1. 
        Eg. if p_value_no == 0, calling get_next_value will return first value.
        if p_value_no == 11, calling get_next_value will return 12-th value."""
        self._data_mgr.goto_value(p_value_no)
        

    def get_next_tag(self):
        """Return next tag to be red.
        Raise data_storage_exceptions.NoNextTag exception if no tags are left."""
        l_tag = self._tags_reader.get_next_tag()
        if not l_tag:
            raise(data_storage_exceptions.NoNextTag())
        return l_tag

    def get_all_tags(self, tag_type=None):
        """Return all tags of type tag_type, or all types if tag_type is None."""
        tags = []
        while True:
            tag = self._tags_reader.get_next_tag()
            if not tag:
                return tags
            if not tag_type or tag_type == tag['name']:
                tags.append(tag)
            

    def get_param(self, p_param_name):
        """Return parameter value for p_param_name.
        Raise NoParameter exception if p_param_name 
        parameters was not found."""
        return self._info_reader.get_param(p_param_name)
