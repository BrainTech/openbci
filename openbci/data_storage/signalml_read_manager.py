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
import sys, struct
import xml.dom.minidom
from openbci.tags import tags_file_reader
from openbci.data_storage import data_storage_exceptions
import info_file_proxy
import data_file_proxy
import data_storage_logging as logger
LOGGER = logger.get_logger("signalml_read_manager")

data_file_extension = ".obci.dat"
info_file_extension = ".obci.info"
tags_file_extension = ".obci.tags"


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
        self._data_reader = data_file_proxy.DataFileReadProxy(p_data_file)
        if len(p_tags_file) == 0:
            self._tags_reader = None            
        else:
            self._tags_reader = tags_file_reader.TagsFileReader(p_tags_file)

    def start_reading(self):
        """Open info file, parse it and remember xml structure. 
        Open data file."""
        LOGGER.info("Try reading info and data file ...")
        self._info_reader.start_reading()
        self._data_reader.start_reading()
        if self._tags_reader:
            self._tags_reader.start_tags_reading()
                
    def get_next_value(self):
        """Return next value from data file (as python float). 
        Close data file and raise NoNextValue exception if eof."""
        return self._data_reader.get_next_value()

    def get_next_tag(self):
        l_tag = self._tags_reader.get_next_tag()
        if not l_tag:
            raise(data_storage_exceptions.NoNextTag())
        return l_tag

    def get_param(self, p_param_name):
        """Return parameter value for p_param_name.
        Raise NoParameter exception if p_param_name 
        parameters was not found."""
        return self._info_reader.get_param(p_param_name)
