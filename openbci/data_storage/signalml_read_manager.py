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

data_file_extension = ".obci.dat"
info_file_extension = ".obci.info"

class NoNextValue(Exception):
    """Raised when end of data file is met in self.get_next_value()."""
    pass

class NoParameter(Exception):
    """Raised when a ther is a requrest for non-existing parameter in info file."""
    def __init__(self, p_param):
        self._param = p_param
    def __str__(self):
        return "No parameter '"+self._param+"' was found in info xml file!"

class SignalmlReadManager(object):
    """A class responsible for reding openbci file format.
    Public interface:
    - start_reading() - open info and data file,
    - get_next_value() - get next value from data file,
    - get_param(param_name) - get param_name parameter from info file.

    Wanna be able to read a new parameter 'new_param'?
    1. Register reading function in self._create_tags_control() under 'new_param' key.
    2. Implement the function (it should be considered as class private function, not callable from outside; 
    the function should return a value for 'new_param' request).
    3. Call get_param('new_param') every time you want to get the param.
    """
    def __init__(self, p_info_file, p_data_file):
        """Just remember info file path and data file path."""
        self._info_file_name = p_info_file
        self._data_file_name = p_data_file
        self._create_tags_control()
    def start_reading(self):
        """Open info file, parse it and remember xml structure. Open data file."""
        l_info_file = ''
        try:
            l_info_file = open(self._info_file_name, 'rt')
        except IOError:
            print("An error occured while opening the info file!")
            sys.exit(1)
        else:
            try:
            #Analyse xml info file, get what we want and close the file.
                self._parse_info_file(l_info_file)
            except xml.parsers.expat.ExpatError:
                l_info_file.close()
                sys.exit(1)
            try:
                self._data_file = open(self._data_file_name, 'rb')
            except IOError:
                l_info_file.close()
                print("An error occured while opening the data file!")
                sys.exit(1)
                
    def get_next_value(self):
        """Return next value from data file (as python float). Close data file and raise NoNextValue exception if eof."""
        l_raw_data = self._data_file.read(8)
        try:
            #TODO - by now it is assumed that error means eof.. What if it is not eof but eg. 4-chars string from the end of a broken file?
            return struct.unpack('d', l_raw_data)[0]
        except struct.error:
            self._data_file.close()
            raise(NoNextValue())
    def get_param(self, p_param_name):
        """Return parameter value for p_param_name.
        Raise NoParameter exception if p_param_name parameters was not found."""
        try:
            return self._tags_control[p_param_name](p_param_name)
        except KeyError:
            raise(NoParameter(p_param_name))

    def _parse_info_file(self, p_info_file):
        """
        Parse p_info_file xml info file and store it in memory.
        Raise exception if the file is not well-formatted.
        """
        #TODO - validate xml regarding dtd
        try:
            self._xml_doc = xml.dom.minidom.parse(p_info_file)
        except Exception, e:
            print("Info file is not a well-formatted xml file. Reading aborted!")
            raise(e)

    def _create_tags_control(self):
        """Register getter functions for signal parameters. See self.__init__ docstring for more details."""
        self._tags_control = {
        'channels_names':self._get_channels_names,
        'file':self._get_file_name,
        'number_of_samples':self._get_simple_param,
        'number_of_channels':self._get_simple_param,
        'sampling_frequency':self._get_simple_param
        }
        
    # Getter methods for info file parameters ****************************************************************************
    def _get_simple_param(self, p_param_name):
        """Return text value from tag in format <param id=p_param_name>text_value</param>."""
        l_params = self._xml_doc.getElementsByTagName('param')
        for i_param in l_params:
            if i_param.getAttribute('id') == p_param_name:
                return i_param.firstChild.nodeValue
    def _get_file_name(self, p_param_name):
        """Return file name from tag <file>file_name</file>."""
        return self._xml_doc.getElementsByTagName(p_param_name)[0].firstChild.nodeValue

    def _get_channels_names(self, p_param_name):
        """
        Return a collection of channel names from tags: 
        <p_param_name><channel_name>name1</channel_name><channel_name>name2</channel_name></p_param_name>.
        """
        l_xml_root_element = self._xml_doc.getElementsByTagName(p_param_name)[0]
        l_channels_names = []
        for i_channel_name_node in l_xml_root_element.childNodes:
            l_channels_names.append(i_channel_name_node.firstChild.nodeValue)
        return l_channels_names
    # Getter methods for info file parameters ****************************************************************************
