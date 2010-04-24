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

import os.path
import xml.dom.minidom

class TagsFileWriter(object):
    """A proxy for openbci tags file, that writes every next tag to file.
    public interface:
    - tag_received(tag_dict)
    - finish_saving()
    """
    def __init__(self, p_file_name, p_dir_path, p_tags_file_extension):
        """Prepare data structure for storing in-memory xml file."""
        self._file_name = os.path.normpath(os.path.join(
                p_dir_path, p_file_name + p_tags_file_extension)) 
        #TODO works in windows and linux on path with spaces?
        self._xml_factory = xml.dom.minidom.Document() 
        #an object useful in the future to easily create xml elements
        self._xml_root = self._xml_factory.createElement(
            'openbci_tags_data_format') 
        #this is going to be an in-memory representation of xml info file
        self._xml_factory.appendChild(self._xml_root)
        self._tags_root = self._xml_factory.createElement('tags')
        self._xml_root.appendChild(self._tags_root)

    def tag_received(self, p_tag_dict):
        """For give dictionary with pirs key -> value create an xml element.
        An exception is with key 'desc' where xml elements are created for
        every element of p_tag_dict['desc'] value which is a dictionary."""
        l_tag = self._xml_factory.createElement('tag')
        for i_key, i_value in p_tag_dict.iteritems():
            if i_key == 'desc':
                for i_k, i_v in i_value.iteritems():
                    l_tag.appendChild(self._create_xml_param_element(
                            i_k, str(i_v)))
            else:
                l_tag.appendChild(self._create_xml_param_element(
                        i_key, str(i_value)))

        self._tags_root.appendChild(l_tag)
                                                 
    def _create_xml_param_element(self, p_key, p_value):
        """Create and return xml element like:
        <param id=p_key value=p_value/>"""
        l_elem = self._xml_factory.createElement('param')
        l_elem.setAttribute('key', p_key)
        l_elem.setAttribute('value', p_value)
        return l_elem

    def finish_saving(self):
        """Write xml tags to the file, return the file`s path."""
        #TODO - lapac bledy
        f = open(self._file_name, 'w')
        f.write(self._xml_factory.toxml('utf-8')) #TODO ustawic kodowanie
        f.close()
        return self._file_name
