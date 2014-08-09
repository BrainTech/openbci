#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from obci.configs import settings
from obci.drivers.generic import py_amplifier_soft

class PyAmplifierVirtual(py_amplifier_soft.PyAmplifierSoft):
    def _manage_params(self):
        super(PyAmplifierVirtual, self)._manage_params()
        chs = self.get_param("active_channels").split(';')
        self.set_param('channel_gains', ';'.join([str(1.0) for i in chs]))
        self.set_param('channel_offsets', ';'.join([str(0.0) for i in chs]))
        #amplifier_name=
        #physical_channels_no=
        #sampling_rates=
        #channels_info=
        self.number_of_channels = int(len(self.get_param("active_channels").split(';')))

    def _get_sample(self):
        ts = None
        sample = []
        for i in range(self.number_of_channels):
            sample.append(random.random()*10*(i+1))
        return sample, ts

if __name__ == "__main__":
    PyAmplifierVirtual(settings.MULTIPLEXER_ADDRESSES).do_sampling()

