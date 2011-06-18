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
import copy
import tags_file_reader
import tags_logging as logger
LOGGER = logger.get_logger("smart_tags_source", "info")


class TagsSource(object):
    def get_tags(self):
        LOGGER.error("The method must be subclassed")

    def _filter_tags(self, p_tags, p_tag_type=None, p_from=None, p_len=None, p_func=None):
        l_tags = p_tags
        if not (p_tag_type is None):
            l_tags = [i_tag for i_tag in l_tags if p_tag_type == i_tag['name']]

        if not (p_from is None):
            l_start = p_from
            l_end = p_from + p_len
            l_tags = [i_tag for i_tag in l_tags if 
                      (l_start <= i_tag['start_timestamp'] and i_tag['start_timestamp'] <= l_end)]

        if not (p_func is None):
            l_tags = [i_tag for i_tag in l_tags if p_func(i_tag)]

        return l_tags
    def __deepcopy__(self, memo):
        return MemoryTagsSource(copy.deepcopy(self.get_tags()))

class MemoryTagsSource(TagsSource):
    def __init__(self, p_tags = None):
        self._tags = None
        if not (p_tags is None):
            self.set_tags(p_tags)
    def set_tags(self, p_tags):
        self._tags = p_tags

    def get_tags(self, p_tag_type=None, p_from=None, p_len=None, p_func=None):
        return self._filter_tags(
            self._tags,
            p_tag_type, p_from, p_len, p_func)
    


class FileTagsSource(TagsSource):
    def __init__(self, p_file_path):
        self._tags_proxy = tags_file_reader.TagsFileReader(p_file_path)

    def get_tags(self, p_tag_type=None, p_from=None, p_len=None, p_func=None):
        return self._filter_tags(
            self._tags_proxy.get_tags(),
            p_tag_type, p_from, p_len, p_func)
        
