#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>
import random, time

from drivers.etr import etr_amplifier
from obci.configs import settings, variables_pb2

class EtrAmplifierDummy(etr_amplifier.EtrAmplifier):
    """A simple class to convey data from multiplexer (UGM_UPDATE_MESSAGE)
    to ugm_engine using udp. That level of comminication is needed, as
    pyqt won`t work with multithreading..."""
    def __init__(self, addresses):
        super(EtrAmplifierDummy, self).__init__(addresses=addresses)
        self._mode = self.get_param("mode")
        self._mode_value = float(self.get_param("mode_value"))
        self._sleep_s = 1/float(self.get_param("sampling_frequency"))
        self.ready()

    def run(self):
        while True:
            time.sleep(self._sleep_s)
            l_msg = variables_pb2.Sample2D()
            if self._mode == "const":
                l_msg.x = self._mode_value
                l_msg.y = self._mode_value
            elif self._mode == "rand":
                l_msg.x = random.random()
                l_msg.y = random.random()
            l_msg.timestamp = time.time()
            
            self.process_message(l_msg)
            
if __name__ == "__main__":
    EtrAmplifierDummy(settings.MULTIPLEXER_ADDRESSES).run()
