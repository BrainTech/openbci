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
import info_file_proxy
import signal_logging as logger
import signal_exceptions
LOGGER = logger.get_logger("read_info_source", "info")

class InfoSource(object):
    def get_param(self, p_key):
        LOGGER.error("The method must be subclassed")
    def get_params(self):
        LOGGER.error("The method must be subclassed")
    def __deepcopy__(self, memo):
        return MemoryInfoSource(copy.deepcopy(self.get_params()))


class MemoryInfoSource(InfoSource):
    def __init__(self, p_params=None):
        self._params = None
        if not (p_params is None):
            self.set_params(p_params)
    def set_params(self, p_params):
        self._params = dict(p_params)

    def set_param(self, p_key, p_value):
        self._params[p_key] = p_value

    def get_param(self, p_key):
        try:
            return self._params[p_key]
        except KeyError:
            raise signal_exceptions.NoParameter(p_key)

    def get_params(self):
        return self._params

class FileInfoSource(InfoSource):
    def __init__(self, p_file):
        try:
            ''+p_file
            LOGGER.debug("Got file path.")
            self._info_proxy = info_file_proxy.InfoFileReadProxy(p_file)
        except TypeError:
            LOGGER.debug("Got file proxy.")
            self._info_proxy = p_file


    def get_param(self, p_key):
        return self._info_proxy.get_param(p_key)
    def get_params(self):
        return self._info_proxy.get_params()
