#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Anna Chabuda <anna.chabuda@gmail.com>

import sys
import pickle

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.analysis.obci_signal_processing import read_manager
from obci.interfaces.biofeedback import biofeedback_calibration_analysis

from obci.configs import settings
from obci.acquisition import acquisition_helper

from obci.utils.openbci_logging import log_crash


class BiofeedbackAnalysis(ConfiguredMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    @log_crash
    def __init__(self, addresses):
        super(BiofeedbackAnalysis, self).__init__(addresses=addresses,
                                          type=peers.LOGIC_P300_CSP)

        self._init_params()

        self.ready()

        self._data_finished = False
        self._info_finished = False
        self._tags_finished = False

    def _init_params(self):
        pass

    def _all_ready(self):
        return self._data_finished and self._info_finished and self._tags_finished

    def handle_message(self, mxmsg):
        if mxmsg.type == types.SIGNAL_SAVER_FINISHED:
            self._data_finished = True
        elif mxmsg.type == types.INFO_SAVER_FINISHED:
            self._info_finished = True
        elif mxmsg.type == types.TAG_SAVER_FINISHED:
            self._tags_finished = True
        else:
            self.logger.warning("Unrecognised message received!!!!")
        self.no_response()

        if self._all_ready():
            self.run()

    def run(self):
        self.logger.info("START Biofeedback Analysis...")

        f_name = self.config.get_param("data_file_name")
        f_dir = self.config.get_param("data_file_path")
        in_file = acquisition_helper.get_file_path(f_dir, f_name)
            
        mgr = read_manager.ReadManager(
            in_file+'.obci.xml',
            in_file+'.obci.raw',
            in_file+'.obci.tag')

        cfg_app = self._get_appconfig(f_dir, f_name)

        fs = float(mgr.get_param("sampling_frequency"))
        channel_names = mgr.get_param("channels_names")
        first_sample_timestamp = float(mgr.get_param('first_sample_timestamp'))

        config = biofeedback_calibration_analysis.run(mgr.get_samples(), cfg_app, channel_names, first_sample_timestamp, fs)

        self._set_config(f_dir, f_name, config)

        self.logger.info("FINISH Biofeedback Analysis...")

        sys.exit(0)

    def _get_appconfig(self, path, name):
        file_name = acquisition_helper.get_file_path(path, name)+'.confapp'
        f = open(file_name, 'r')
        cfg = pickle.load(f)
        f.close()
        return cfg

    def _set_config(self, path, name, config):
        config_file = acquisition_helper.get_file_path(path, name)+'.conf'
        f = open(config_file, 'w')
        pickle.dump(config, f)
        f.close()

if __name__ == "__main__":
    BiofeedbackAnalysis(settings.MULTIPLEXER_ADDRESSES).loop()
