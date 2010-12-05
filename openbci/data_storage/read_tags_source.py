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

from tags import tags_file_reader
import data_storage_logging as logger
LOGGER = logger.get_logger("smart_tags_source", "info")


class TagsSource(object):
    def get_tags(self):
        LOGGER.error("The method must be subclassed")


class FileTagsSource(TagsSource):
    def __init__(self, p_file_path):
        self._tags_proxy = tags_file_reader.TagsFileReader(p_file_path)

    def get_tags(self):
        return self._tags_proxy.get_tags()
        
