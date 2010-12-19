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
import sys, struct, time, numpy, copy

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
            LOGGER.debug("Got info source file path.")
            self.info_source = read_info_source.FileInfoSource(p_info_source)
        except TypeError:
            LOGGER.debug("Got info source object.")
            self.info_source = p_info_source

        try:
            ''+p_data_source
            LOGGER.debug("Got data source file path.")
            self.data_source = read_data_source.FileDataSource(
                p_data_source,
                int(self.info_source.get_param('number_of_channels'))
                )
        except TypeError:
            LOGGER.debug("Got data source object.")
            self.data_source = p_data_source

        try:
            ''+p_tags_source
            LOGGER.debug("Got tags source file path.")
            self.tags_source = read_tags_source.FileTagsSource(p_tags_source)
        except TypeError:
            LOGGER.debug("Got tags source object.")
            self.tags_source = p_tags_source 

    def __deepcopy__(self, memo):
        info_source = copy.deepcopy(self.info_source)
        tags_source = copy.deepcopy(self.tags_source)
        samples_source = copy.deepcopy(self.data_source)
        return ReadManager(info_source, samples_source, tags_source)
        
    def get_samples(self, p_from=None, p_len=None):
        """Return a two dimensional array of signal values.
        if p_reload then refresh the file, otherwise use cached values."""
        
        return self.data_source.get_samples(p_from, p_len)

    def get_channel_samples(self, p_ch_name, p_from=None, p_len=None):
        """Return an array of values for channel p_ch_name, or
        raise ValueError exception if there is channel with that name."""
        ch_ind = self.get_param('channels_names').index(p_ch_name) #TODO error
        return self.get_samples(p_from, p_len)[ch_ind]

    def get_tags(self, p_tag_type=None, p_from=None, p_len=None, p_func=None):
        """Return all tags of type tag_type, or all types if tag_type is None."""

        if self.tags_source is None:
            return []
        else:
            return self.tags_source.get_tags(p_tag_type, p_from, p_len, p_func)

    def get_param(self, p_param_name):
        """Return parameter value for p_param_name.
        Raise NoParameter exception if p_param_name 
        parameters was not found."""
        return self.info_source.get_param(p_param_name)

    def get_params(self):
        return self.info_source.get_params()

    def iter_tags(self, p_tag_type=None, p_from=None, p_len=None, p_func=None):
        if self.tags_source is None:
            return 

        for tag in self.tags_source.get_tags(p_tag_type, p_from, p_len, p_func):
            yield tag
        
    def iter_samples(self):
        for s in self.data_source.iter_samples():
            yield s
