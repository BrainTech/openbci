# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

from data_generic_write_proxy import DataGenericWriteProxy
BUF_SIZE = 1024

class DataBufferedWriteProxy(DataGenericWriteProxy):
    def __init__(self, p_file_path, p_unpack_later=False, p_append_ts=False, p_sample_type='FLOAT'):
        """Open p_file_name file in p_dir_path directory."""
        self.buffer = [0.0]*BUF_SIZE
        super(DataBufferedWriteProxy, self).__init__(p_file_path, p_unpack_later, p_append_ts, p_sample_type)

    def data_received(self, p_data):
        """ p_data must be protobuf SampleVector message, but serialized to string.
        Data is stored in temp buffer, once a while the buffer is flushed to a file."""
        ind = self._number_of_samples % BUF_SIZE
        self.buffer[ind] = p_data
        self._number_of_samples = self._number_of_samples + 1
        if (ind + 1) == BUF_SIZE:
                self._write_buffer()

    def _write_buffer(self):
        if self._unpack_later:
            self._write_file(''.join(self.buffer))
        else:
            for d in self.buffer:
                self._write_file(self._vect_to_string(d))

    def finish_saving(self):
        """Close the file, return a tuple - 
        file`s name and number of samples."""
        self._write_file(''.join(self.buffer[:(self._number_of_samples % BUF_SIZE)]))
        return super(DataBufferedWriteProxy, self).finish_saving()
