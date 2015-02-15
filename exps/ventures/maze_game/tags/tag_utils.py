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
#      Mateusz Kruszynski <mateusz.kruszynski@gmail.com>
#


def unpack_tag_from_dict(p_dict):
    """For given dictinary describing tag in strings, return dictionary
    where numeric values are numbers, not strings.
    The method is fired by file tags reader, while parsing xml tags file."""
    l_tag_dict = {}
    l_tag_dict['start_timestamp'] = float(p_dict['position'])
    l_tag_dict['end_timestamp'] = l_tag_dict['start_timestamp'] + float(p_dict['length'])
    l_tag_dict['name'] = p_dict['name']
    ch_str = p_dict['channelNumber']
    try:
        ch = float(ch_str)
        if ch == -1.0:
            ch_str = ''
    except ValueError:
        pass
        
    l_tag_dict['channels'] = ch_str
    l_tag_desc = {}
    for i_key, i_value in p_dict.iteritems():
        if i_key not in ['position', 'length', 'name', 'channelNumber']:
            # TODO - use tag definition in case i_value is not a string
            # but some more complex structure
            l_tag_desc[i_key] = i_value
    l_tag_dict['desc'] = l_tag_desc
    return l_tag_dict

def pack_tag_to_dict(p_start_timestamp, p_end_timestamp, 
                 p_tag_name, p_tag_desc={}, p_tag_channels=""):
    """For given tag parameters return a dictionary representing
    tag with those parameters.
    Parameters:
    - p_start_timestamp - float 
    - p_end_timestamp - float
    - p_tag_name - string
    - p_tag_desc - dictionary
    - p_tag_channels - string like "0 6 7" - numbers of channels
    """
    l_tag_dict = {}
    l_tag_dict['start_timestamp'] = p_start_timestamp
    l_tag_dict['end_timestamp'] = p_end_timestamp
    l_tag_dict['name'] = p_tag_name
    l_tag_dict['channels'] =p_tag_channels
    l_tag_dict['desc'] = p_tag_desc

    return l_tag_dict
