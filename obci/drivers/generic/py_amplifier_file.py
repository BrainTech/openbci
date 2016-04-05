#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random, os
from  obci.analysis.obci_signal_processing import read_manager
from obci.configs import settings
from obci.drivers.generic import py_amplifier_soft

class PyAmplifierFile(py_amplifier_soft.PyAmplifierSoft):
    def _manage_files(self):
        self.f_data = os.path.expanduser(os.path.join(
            self.config.get_param('data_file_dir'), 
            self.config.get_param('data_file_name'))+'.obci.raw')

        i_dir = self.config.get_param('info_file_dir')
        if len(i_dir) == 0:
            i_dir = self.config.get_param('data_file_dir')
        i_name = self.config.get_param('info_file_name')
        if len(i_name) == 0:
            i_name = self.config.get_param('data_file_name')
        self.f_info = os.path.expanduser(os.path.join(i_dir, i_name)+'.obci.xml')

        t_dir = self.config.get_param('tags_file_dir')
        if len(t_dir) == 0:
            t_dir = self.config.get_param('data_file_dir')
        t_name = self.config.get_param('tags_file_name')
        if len(t_name) == 0:
            t_name = self.config.get_param('data_file_name')
        self.f_tags = os.path.expanduser(os.path.join(t_dir, t_name)+'.obci.tag')

    def _manage_params(self):
        self._manage_files()
        mgr = read_manager.ReadManager(self.f_info, self.f_data, self.f_tags)
        self.set_param('sample_type', mgr.get_param('sample_type'))
        self.set_param('sampling_rate', str(int(float(mgr.get_param('sampling_frequency')))))
        self.set_param('channel_names', ';'.join(mgr.get_param('channels_names')))
        self.set_param('active_channels', self.get_param('channel_names'))
        self.set_param('channel_gains', ';'.join(mgr.get_param('channels_gains')))
        self.set_param('channel_offsets', ';'.join(mgr.get_param('channels_offsets')))

        self._samples = mgr.get_samples()
        self._tags = mgr.get_tags()
        self._ind = 0
        super(PyAmplifierFile, self)._manage_params()

    def _get_sample(self):
        ts = None
        try:
            sample = list(self._samples[:, self._ind])
        except IndexError:
            return None, None
        else:
            self._ind += 1
            return sample, ts
            
    def _post_send(self):
        pass
        #TODO - send tags if it is the right titm

if __name__ == "__main__":
    PyAmplifierFile(settings.MULTIPLEXER_ADDRESSES).do_sampling()

