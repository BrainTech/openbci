# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

from data_generic_write_proxy import DataGenericWriteProxy

class DataAsciWriteProxy(DataGenericWriteProxy):
    def data_received(self, p_data):
        self._write_file(repr(p_data)+'\n')
        self._number_of_samples = self._number_of_samples + 1





