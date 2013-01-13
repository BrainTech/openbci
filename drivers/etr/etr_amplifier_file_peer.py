#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>
import random, time, os.path, sys

from obci.drivers.etr import etr_amplifier
from obci.configs import settings, variables_pb2
from obci.analysis.obci_signal_processing.signal import data_read_proxy

class EtrAmplifierFile(etr_amplifier.EtrAmplifier):
    def __init__(self, addresses):
        super(EtrAmplifierFile, self).__init__(addresses=addresses)
        l_path = os.path.expanduser(os.path.normpath(self.get_param("file_path")))
        file_proxy = data_file_proxy.DataReadProxy(l_path)
        self.file_buf = file_proxy.get_all_values(2)
        self.file_buf_ind = 0
        file_proxy.finish_reading()
        self._sleep_s = 1/float(self.get_param("sampling_freqency"))
        self.ready()

    def run(self):
        while True:
            time.sleep(self._sleep_s)
            if self.file_buf_ind == len(self.file_buf[0]):
                self.logger.info("END OF FILE!")
                sys.exit(0)
            else:
                l_msg = variables_pb2.Sample2D()
                l_msg.x = self.file_buf[0, self.file_buf_ind]
                l_msg.y = self.file_buf[1, self.file_buf_ind]
                l_msg.timestamp = time.time()
                self.file_buf_ind += 1
                self.process_message(l_msg)

if __name__ == "__main__":
    EtrAmplifierFile(settings.MULTIPLEXER_ADDRESSES).run()

