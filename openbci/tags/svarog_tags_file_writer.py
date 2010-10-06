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
from openbci.core import types_utils


TAG_STYLES = {
    'gray': {'fill_color':'808080',
             'outline_color':'808080',
             'outline_width':'1.0',
             'outline_dash':'',
             'key_shortcut':'Shift b',
             'marker':'0'
             },
    'red': {'fill_color':'ff0000',
             'outline_color':'808080',
             'outline_width':'1.0',
             'outline_dash':'',
             'key_shortcut':'Shift b',
             'marker':'0'
             },
    'blue': {'fill_color':'0017ff',
             'outline_color':'808080',
             'outline_width':'1.0',
             'outline_dash':'',
             'key_shortcut':'Shift b',
             'marker':'0'
             },



    }

TAG_DEFS = {
    'default': 'gray',
    'word': 'red',
    'mask2': 'blue'
    }
class SvarogTagsFileWriter(object):
    """A proxy for openbci tags file, that writes every next tag to file.
    public interface:
    - tag_received(tag_dict)
    - finish_saving()
    """
    def __init__(self, p_file_name, p_dir_path, p_tags_file_extension,
                 p_sampling_rate,  p_num_of_channels,
                 p_defs = [{'name':'default', 
                            'description':'default description'}]
                 ):
        """Prepare data structure for storing in-memory xml file."""

        #Store below values to compute svarog-style tag params: 
        #Length of tag, its starting time in seconds, relative to 
        #the beginning of the signal
        self._sampling_rate = p_sampling_rate
        self._num_of_channels = p_num_of_channels

        self._file_name = os.path.normpath(os.path.join(
                p_dir_path, p_file_name + p_tags_file_extension)) 
        #TODO works in windows and linux on path with spaces?
        self._xml_factory = xml.dom.minidom.Document() 
        #an object useful in the future to easily create xml elements
        self._xml_root = self._xml_factory.createElement(
            'annotations') 
        #this is going to be an in-memory representation of xml info file
        self._xml_factory.appendChild(self._xml_root)

        self._init_default_tags()
        self._init_tags_defs(p_defs)

        #create 'tags' tag structure
        l_td = self._xml_factory.createElement('tag_data')
        self._xml_root.appendChild(l_td)
        self._tags_root = self._xml_factory.createElement('tags')
        l_td.appendChild(self._tags_root)

    def _init_default_tags(self):
        l_pg = self._xml_factory.createElement('paging')
        l_pg.setAttribute('page_size', '20.0')
        l_pg.setAttribute('blocks_per_page', '5')
        self._xml_root.appendChild(l_pg)

    def _init_tags_defs(self, p_defs):
        """Create structure:
        <tag_definitions>
           <def_group "name"="channelTags">
              <tag_item .... />
           </def_group>
        </tag_definitions>
        
        tag_item paramteres are taken from TAG_DEFS.
        """
        l_td = self._xml_factory.createElement('tag_definitions')
        self._xml_root.appendChild(l_td)

        l_tgr = self._xml_factory.createElement('def_group')
        l_tgr.setAttribute('name', 'channelTags')
        l_td.appendChild(l_tgr)

        for i_def in p_defs:
            l_item = self._xml_factory.createElement('tag_item')
            # Set name and description
            for i_key, i_value in i_def.iteritems():
                l_item.setAttribute(i_key, i_value)
                
            # Set styles
            l_styles = TAG_STYLES[TAG_DEFS[i_def['name']]]
            for i_key, i_value in l_styles.iteritems():
                l_item.setAttribute(i_key, i_value)                
            l_tgr.appendChild(l_item)

    def set_first_sample_timestamp(self, p_ts):
        self._first_sample_timestamp = p_ts
    def tag_received(self, p_tag_dict):
        """For give dictionary with pirs key -> value create an xml element.
        An exception is with key 'desc' where xml elements are created for
        every element of p_tag_dict['desc'] value which is a dictionary."""

        l_tag_params = {}
        l_tag_params['name'] = self._get_tag_def_for(p_tag_dict['name'])
        l_tag_params['length'] = max(
            float(p_tag_dict['end_timestamp']) - \
            float(p_tag_dict['start_timestamp']),
            0.02)
        l_tag_params['position'] = float(p_tag_dict['start_timestamp']) - \
            self._first_sample_timestamp
        for i_channel in range(self._num_of_channels):
            l_tag = self._xml_factory.createElement('tag')
            l_tag.setAttribute('channel_number', str(i_channel))
            for i_key, i_value in l_tag_params.iteritems():
                l_tag.setAttribute(i_key, types_utils.to_string(i_value))
            self._tags_root.appendChild(l_tag)


    def _get_tag_def_for(self, p_tag_name):
        if p_tag_name in TAG_DEFS.keys():
            return p_tag_name
        else:
            return 'default'

    def finish_saving(self):
        """Write xml tags to the file, return the file`s path."""
        #TODO - lapac bledy
        f = open(self._file_name, 'w')
        f.write(self._xml_factory.toxml('utf-8')) #TODO ustawic kodowanie
        f.close()
        return self._file_name
