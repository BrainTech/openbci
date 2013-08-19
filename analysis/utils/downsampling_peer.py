#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from os import listdir
from os.path import isfile, join

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient
from obci.configs import settings, variables_pb2

from obci.analysis.obci_signal_processing import read_manager
from obci.acquisition import acquisition_helper
import numpy as np


class Downsampling(ConfiguredClient):
    def __init__(self, addresses):

        super(Downsampling, self).__init__(addresses=addresses, type=peers.CLIENT)
        self.new_fs = int(float(self.config.get_param("new_sampling_freq")))
        file_name = self.config.get_param("file_name")
        self.file_path = self.config.get_param("file_path")

        if not file_name:
            _file = acquisition_helper.get_file_path(self.file_path, file_name)

            try:
                files = [f for f in listdir(_file) if isfile(join(_file, f))]
            except OSError:
                self.logger.error("No such file or directory: {}".format(_file))
                sys.exit(1)

            self.old_file = [f.split(".")[0] for f in files if "raw" in f]
            self.logger.info("Prepered to resampling {} files from {}... \n files list: {}".format(len(self.old_file), self.file_path, self.old_file))

        else:
            self.old_file = [file_name]
            self.logger.info("Prepered to resampling {} file from {}...".format(self.old_file[0], self.file_path))
        self.ready()

    def make_new_file(self, old_file):

        in_file = acquisition_helper.get_file_path(self.file_path, old_file)

        try:
            manager = read_manager.ReadManager(in_file+".obci.xml",
                                               in_file+".obci.raw",
                                               in_file+".obci.tag")
        except IOError:
            self.logger.error("No such file or directory: {}".format(in_file))
            sys.exit(1)

        fs = int(float(manager.get_param("sampling_frequency")))
        data = manager.get_samples()
        self.logger.info("START resampling: file: {}, old_fs = {} Hz, new_fs = {} Hz...".format(old_file, fs, self.new_fs))
        
        if not fs % new_fs == 0:
            self.logger.error("WRONG new sampling frequency!!\n You can choose sampling frequency, which is the divisor of old sampling frequency")
            sys.exit(0)
        else:
            sample_step = fs/self.new_fs

        new_data = np.array([data[:,i] for i in range(0, data.shape[1], sample_step)]).T
        manager.set_samples(new_data, manager.get_param("channels_names"))
        manager.set_param("sampling_frequency", str(self.new_fs))
        self.logger.info("FINISH resampling: file: {}, old_fs = {} Hz, new_fs = {} Hz".format(old_file, fs, self.new_fs))
        self.logger.info("START saving data to {}...".format(in_file + "_resampling_to_"+str(self.new_fs)))
        manager.save_to_file(self.file_path, in_file + "_resampling_to_"+str(self.new_fs))
        self.logger.info("FINISH saving new data")

    def run(self):

        for old_file in self.old_file:
            self.make_new_file(old_file)

if __name__ == "__main__":
    Downsampling(settings.MULTIPLEXER_ADDRESSES).run()
