# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

from data_generic_write_proxy import DataGenericWriteProxy

class DataSimpleWriteProxy(DataGenericWriteProxy):
    def data_received(self, p_data):
        if self._unpack_later:
            self._write_file(p_data)
        else:
            self._write_file(self._vect_to_string(p_data))
        self._number_of_samples = self._number_of_samples + 1
