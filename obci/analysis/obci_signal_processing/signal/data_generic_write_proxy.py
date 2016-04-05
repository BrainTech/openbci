# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

import struct
import sys, os.path
from obci.configs import variables_pb2

import signal_exceptions
import signal_constants
import signal_logging as logger
LOGGER = logger.get_logger("data_generic_write_proxy", 'info')

SAMPLE_STRUCT_TYPES = signal_constants.SAMPLE_STRUCT_TYPES

class DataGenericWriteProxy(object):
    """
    A class representing data file. 
    It should be an abstraction for saving raw data into a file. 
    Decision whether save signal to one or few separate files should be made here 
    and should be transparent regarding below interface - the interface should remain untouched.
    Public interface:
    - finish_saving() - closes data file and return its path,
    - data_received(p_data_sample) - gets and saves next sample of signal
    """
    def __init__(self, p_file_path, p_unpack_later=False, p_append_ts=False, p_sample_type='FLOAT'):
        """Open p_file_name file in p_dir_path directory."""
        self._number_of_samples = 0
        self._unpack_later = p_unpack_later
        self._append_ts = p_append_ts
        self._file_path = p_file_path
        self._sample_struct_type = SAMPLE_STRUCT_TYPES[p_sample_type]

        try:
            if self._unpack_later:
            # Create a temporary file with .tmp extension
            # In finish_saving we read from that file and create another 
            # for efficency reasons
                self._file = open(self._file_path+'.tmp', 'wb') #open file in a binary mode
            else:
                self._file = open(self._file_path, 'wb') #open file in a binary mode

        except IOError:
            LOGGER.error("Error! Can`t create a file!!!. path: " +
                         str(self._file_path))
            sys.exit(1)

    def data_received(self, p_data):
        raise Exception("To be subclassed")

    def set_data_len(self, ln, sm):
        """Set length of one unit of protobuf data
        stored in temporary file. It`ll be useful
        in finish_saving() while extracting data from the file."""
        self._data_len = ln
        self._samples_per_vector = sm

    def set_first_sample_timestamp(self, timestamp):
        self.first_sample_timestamp = timestamp

    def finish_saving(self):
        """Close the file, return a tuple - 
        file`s name and number of samples."""
        self._file.flush()
        self._file.close()

        if self._unpack_later:
            return self._unpack_and_finish()
        else:
            return self._file_path, self._number_of_samples

    def _unpack_and_finish(self):

        final_file = open(self._file_path, 'w')
        # Open once more temporary file with protobuf data
        temp_file = open(self._file_path+'.tmp', 'r')
        while True:
            msg = temp_file.read(self._data_len)
            if len(msg) == 0:
                break
            self._write_file(self._vect_to_string(msg), final_file)

        final_file.flush()
        final_file.close()
        
        # Close and remove temporary file
        temp_file.close()
        os.remove(self._file_path+'.tmp')

        return self._file_path, self._number_of_samples

    def _write_file(self, str_data, f=None):
        try:
            if f:
                f.write(str_data)
            else:
                self._file.write(str_data)
        except ValueError:
            LOGGER.error("Warning! Trying to write data to closed data file!")
            return

    def _vect_to_string(self, p_mx_vect):
        l_vec = variables_pb2.SampleVector()
        l_vec.ParseFromString(p_mx_vect)
        samples = []
        for j in range(len(l_vec.samples)):
            s = l_vec.samples[j]
            ts = s.timestamp
            try:
                strs = [struct.pack(self._sample_struct_type, ch) for ch in s.channels]
                if self._append_ts:
                    strs.append(struct.pack(self._sample_struct_type, ts-self.first_sample_timestamp))
            except struct.error:
                LOGGER.error("Error while writhing to file. Bad sample format.")
                raise(signal_exceptions.BadSampleFormat())

            samples.append(''.join(strs))
        return ''.join(samples)
