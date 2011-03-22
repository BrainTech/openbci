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
import numpy, copy
import data_file_proxy
import data_storage_logging as logger
import data_storage_exceptions
LOGGER = logger.get_logger("data_source", "info")

class DataSource(object):
    def get_samples(self, p_from=None, p_len=None):
        LOGGER.error("The method must be subclassed")

    def iter_samples(self):
        LOGGER.error("The method must be subclassed") 
    def __deepcopy(self, memo):
        return MemoryDataSource(copy.deepcopy(self.get_samples()))



class MemoryDataSource(DataSource):
    def __init__(self, p_data=None, p_copy=True):
        self._data = None

        if not (p_data is None):
            self.set_samples(p_data, p_copy)

    def set_samples(self, p_data, p_copy=True):
        if p_copy:
            self._data = numpy.array(p_data)
        else:
            self._data = p_data

    def set_sample(self, p_sample_index, p_sample):
        """
        Throws:
        - IndexError if p_sample_index is out of range
        - ValueError if len(p_sample) doesn`t fit number_of_channels
        """
        self._data[:, p_sample_index] = p_sample
            
    def get_samples(self, p_from=None, p_len=None):
        """
        Always success. If p_from or p_len is somehow out of range
        return an empty array of samples
        """
        if p_from is None:
            return self._data
        else:
            return self._data[:, p_from:(p_from+p_len)]

    def iter_samples(self):
        for i in range(len(self._data[0])):
            yield self._data[:, i]
    

class FileDataSource(DataSource):
    def __init__ (self, p_file, p_num_of_channels):
        self._num_of_channels = p_num_of_channels
        self._mem_source = None 
        try:
            ''+p_file
            LOGGER.debug("Got file path.")
            self._data_proxy = data_file_proxy.DataFileReadProxy(p_file)
        except TypeError:
            LOGGER.debug("Got file proxy.")
            self._data_proxy = p_file


    def get_samples(self, p_from=None, p_len=None):
        if self._mem_source:
            # we have data in-memory
            return self._mem_source.get_samples(p_from, p_len)
        elif p_from is None:
            # we dont have data in-memory
            # and whole data set is reqested
            # so let`s use the ocasion and cache data
            LOGGER.info("All data set requested for the first time. Start reading all data from the file...")
            vals = self._data_proxy.get_all_values(self._num_of_channels)
            self._mem_source = MemoryDataSource(vals, False)
            return self._mem_source.get_samples()

        else:
            # we dont have data in-memory
            # only a piece of data is requested
            ret = numpy.zeros((self._num_of_channels, p_len))
            self._data_proxy.goto_value(p_from*self._num_of_channels)
            for i in range(p_len):
                ret[:, i] =  self._data_proxy.get_next_values(self._num_of_channels)
            return ret
            
    
    def iter_samples(self):
        if self._mem_source:
            for samp in self._mem_source.iter_samples():
                yield samp
        else:
            self._data_proxy.finish_reading()
            self._data_proxy.start_reading()
            while True:
                try:
                    samp = numpy.zeros(self._num_of_channels)
                    samp[:] = self._data_proxy.get_next_values(self._num_of_channels)
                    yield samp
                except data_storage_exceptions.NoNextValue:
                    break
