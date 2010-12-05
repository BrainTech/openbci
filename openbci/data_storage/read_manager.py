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

from openbci.data_storage import data_storage_exceptions


from openbci.data_storage import read_data_source
from openbci.data_storage import read_info_source
from openbci.data_storage import read_tags_source

import data_storage_logging as logger
LOGGER = logger.get_logger("read_manager", "info")

class ReadManager(object):
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
    def __init__(self, p_info_source, p_data_source, p_tags_source):
        """Just remember info file path and data file path."""
        try:
            ''+p_info_source
            LOGGER.info("Got info source file path.")
            self._info_source = read_info_source.FileInfoSource(p_info_source)
        except TypeError:
            LOGGER.info("Got info source object.")
            self._info_source = p_info_source

        try:
            ''+p_data_source
            LOGGER.info("Got data source file path.")
            self._data_source = read_data_source.FileDataSource(
                p_data_source,
                int(self._info_source.get_param('number_of_channels'))
                )
        except TypeError:
            LOGGER.info("Got data source object.")
            self._data_source = p_data_source

        try:
            ''+p_tags_source
            LOGGER.info("Got tags source file path.")
            self._tags_source = read_tags_source.FileTagsSource(p_tags_source)
        except TypeError:
            LOGGER.info("Got tags source object.")
            self._tags_source = p_tags_source 

        #TODO - wszystko start reading

    def get_iterator(self):
        return ReadManagerIterator(self)

    def get_samples(self, p_from=None, p_len=None):
        """Return a two dimensional array of signal values.
        if p_reload then refresh the file, otherwise use cached values."""
        
        return self._data_source.get_samples(p_from, p_len)

    def get_channel_samples(self, p_ch_name, p_from=None, p_len=None):
        """Return an array of values for channel p_ch_name, or
        raise ValueError exception if there is channel with that name."""
        ch_ind = self.get_param('channels_names').index(p_ch_name) #TODO error
        return self.get_samples(p_from, p_len)[ch_ind]

    def get_tags(self, p_tag_type=None):
        """Return all tags of type tag_type, or all types if tag_type is None."""

        if self._tags_source is None:
            return []

        l_tags = self._tags_source.get_tags()
        if not p_tag_type:
            return l_tags

        l_ret_tags = []
        for i_tag in l_tags:
            if p_tag_type == i_tag['name']:
                l_ret_tags.append(i_tag)
        return l_ret_tags

    def get_param(self, p_param_name):
        """Return parameter value for p_param_name.
        Raise NoParameter exception if p_param_name 
        parameters was not found."""
        return self._info_source.get_param(p_param_name)

    def iter_tags(self):
        if self._tags_source is None:
            return 

        for tag in self._tags_source.get_tags():
            yield tag
        
    def iter_samples(self):
        for s in self._data_source.iter_samples():
            yield s
