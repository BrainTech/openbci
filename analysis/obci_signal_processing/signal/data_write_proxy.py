# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
import data_buffered_write_proxy
import data_simple_write_proxy
import data_raw_write_proxy
import data_asci_write_proxy

import signal_logging as logger
LOGGER = logger.get_logger("data_write_proxy", 'info')

def get_proxy(file_path, append_ts=False, use_tmp_file=False, use_own_buffer=False, format='FLOAT'):
    if format == 'FLOAT' or format == 'DOUBLE':
        if use_own_buffer:
            return data_buffered_write_proxy.DataBufferedWriteProxy(
                file_path, use_tmp_file, append_ts, format)
        else:
            return data_simple_write_proxy.DataSimpleWriteProxy(
                file_path, use_tmp_file, append_ts, format)
    else:
        LOGGER.warning("For non-mx types all other parameters are ignored!!!")
        if format == 'raw':
            return data_raw_write_proxy.DataRawWriteProxy(file_path)
        elif format == 'asci':
            return data_asci_write_proxy.DataAsciWriteProxy(file_path)        
        else:
            raise Exception("Unknow format: "+str(format))

