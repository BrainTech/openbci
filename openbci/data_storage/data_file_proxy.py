# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 200SAMPLE_SIZE-2009 Krzysztof Kulewski and Magdalena Michalska
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

import struct
import sys
import os.path
from openbci.data_storage import data_storage_exceptions
from openbci.data_storage import data_storage_logging as logger
LOGGER = logger.get_logger("data_file_proxy", 'debug')
import time
SAMPLE_SIZE = 8 #float
class DataFileWriteProxy(object):
    """
    A class representing data file. 
    It should be an abstraction for saving raw data into a file. 
    Decision whether save signal to one or few separate files should be made here 
    and should be transparent regarding below interface - the interface should remain untouched.
    Public interface:
    - finish_saving() - closes data file and return its path,
    - data_received(p_data_sample) - gets and saves next sample of signal
    """
    def __init__(self, p_file_name, p_dir_path, p_file_extension):
        """Open p_file_name file in p_dir_path directory."""
        self._number_of_samples = 0
        self._file_name = os.path.normpath(os.path.join(
                p_dir_path, p_file_name + p_file_extension))
        #TODO works in windows and linux on path with spaces?
        try:
            #TODO - co jesli plik istnieje?
            self._file = open(self._file_name, 'wr') #open file in a binary mode
        except IOError:
            LOGGER.error("Error! Can`t create a file!!!.")
            sys.exit(1)
        self.t_wr = 0.0
        self.t_fl = 0.0
        self.t_full = 0.0

    def finish_saving(self):
        """Close the file, return a tuple - 
        file`s name and number of samples."""
        self._file.flush()
        self._file.close()
        return self._file_name, self._number_of_samples

    def data_received(self, p_data):
        """ Write p_data t self._file as raw float(C++ double). Here we assume, that
        p_data is of float type. 
        Type verification should be conducted earlier."""
        try:
            self._file.write(struct.pack("d", p_data)) 
        except ValueError:
            LOGGER.error("Warning! Trying to write data to closed data file!")
            return
        except struct.error:
            LOGGER.error("Error while writhing to file. Bad sample format.")
            raise(data_storage_exceptions.BadSampleFormat())

        #store number of samples
        self._number_of_samples = self._number_of_samples + 1


class AsciFileWriteProxy(object):
    def __init__(self, p_file_name, p_dir_path, p_file_extension):
        """Open p_file_name file in p_dir_path directory."""
        self._file_name = os.path.normpath(os.path.join(
                p_dir_path, p_file_name + p_file_extension))
        try:
            self._file = open(self._file_name, 'w') #open file in a binary mode
        except IOError:
            print "Error! Can`t create a file!!!."
            sys.exit(1)

    def finish_saving(self):
        """Close the file, return a tuple - 
        file`s name and number of samples."""
        self._file.close()
        return self._file_name

    def data_received(self, p_data):
        """ Write p_data t self._file as raw int. Here we assume, that
        p_data is of float type. 
        Type verification should be conducted earlier."""
        try:
            self._file.write(repr(p_data)+'\n')
        except ValueError:
            print("Warning! Trying to write data to closed data file!")
            return
        
        self._file.flush()


class DataFileReadProxy(object):
    def __init__(self, p_file_path):
        self._file_path = p_file_path
        
    def start_reading(self):
        try:
            self._data_file = open(self._file_path, 'rb')
        except IOError, e:
            LOGGER.error("An error occured while opening the data file!")
            raise(e)
    def get_next_value(self):
        """Return next value from data file (as python float). 
        Close data file and raise NoNextValue exception if eof."""
        l_raw_data = self._data_file.read(SAMPLE_SIZE)
        try:
            #TODO - by now it is assumed that error means eof.. 
            #What if it is not eof but eg. 4-chars 
            #string from the end of a broken file?
            return struct.unpack('d', l_raw_data)[0]
        except struct.error:
            self._data_file.close()
            raise(data_storage_exceptions.NoNextValue())
        except Exception, e:
            raise(e)

    def goto_value(self, p_value_no):
        """Set the engine, so that nex 'get_next_value' call will return
        value number p_value_no+1. 
        Eg. if p_value_no == 0, calling get_next_value will return first value.
        if p_value_no == 11, calling get_next_value will return 12-th value."""
        LOGGER.debug("DOING SEEK TO: "+str(p_value_no))
        self._data_file.seek(p_value_no * SAMPLE_SIZE)
        LOGGER.debug("DATA FILE SEEK DONE. CURRENT POSITION/8 = "+str(self._data_file.tell()/8))

