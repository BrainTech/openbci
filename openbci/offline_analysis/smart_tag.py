#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

"""Implement Smart tags classes: SmartTagEndTag, SmartTagDuration."""

class SmartTag(object):
    def __init__(self, p_tag_def, p_start_tag):
        self._data = []
        self._start_tag = p_start_tag
        self._tag_def = p_tag_def
        
    def get_start_timestamp(self):
        return self._start_tag['start_timestamp'] + \
            self._tag_def.start_offset

    def get_end_timestamp(self):
        pass
    
    def get_start_tag(self):
        return self._start_tag

    def get_data(self):
        """Return stored data. It is a list in format: 
        [[list of all samples from ch 0], [list of all samples from ch 1] ...]
        """
        return self._data

    def get_data_for(self, p_ch_num):
        return self._data[p_ch_num]

    def set_data(self, p_data):
        self._data = p_data

class SmartTagEndTag(SmartTag):
    """Public interface:
    - get_data() <- this is the only method to be really used outside
    -
    - __init__(tag_def, start_tag)
    - get_start_timestamp()
    - get_end_timestamp()
    - get_data_for(channel)
    - get_start_tag()
    - get_end_tag()
    - set_data()
    - set_end_tag()
    """
    def __init__(self, p_tag_def, p_start_tag):
        """l
        - p_tag_def - must be an instance of SmartTagEndTagDefinition.
        - p_start_tag - must be a dictionary representaion of existing tag.
        """
        super(SmartTagEndTag, self).__init__(p_tag_def, p_start_tag)
        self._end_tag = None

    def set_end_tag(self, p_tag):
        """This method must be fired only and only once, to set 
        smart tag`s ending tag."""
        self._end_tag = p_tag

    def get_end_timestamp(self):
        return self._end_tag['start_timestamp'] + self._tag_def.end_offest

class SmartTagDuration(SmartTag):
    """Public interface:
    - get_data() <- this is the only method to be really used outside
    - 
    - __init__(tag_def, start_tag)
    - get_start_timestamp()
    - get_end_timestamp()
    - get_data_for(channel)
    - get_start_tag()
    - set_data()
    - set_end_tag()
    """
    def __init__(self, p_tag_def, p_start_tag):
        """
        - p_tag_def - must be an instance of SmartTagDurationDefinition.
        - p_start_tag - must be a dictionary representaion of existing tag.
        """
        super(SmartTagDuration, self).__init__(p_tag_def, p_start_tag)

    def get_end_timestamp(self):
        return self._start_tag['start_timestamp'] + \
            self._tag_def.duration + self._tag_def.end_offset


 
