#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Anna Chabuda <anna.chabuda@gmail.com>

import time, sys, pickle

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.configs import settings, variables_pb2
from obci.acquisition import acquisition_helper
from obci.interfaces.biofeedback import biofeedback_calibration

class BiofeedbackCalibration(ConfiguredMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        super( BiofeedbackCalibration, self).__init__(addresses=addresses,
                                          type=peers.LOGIC_P300_CALIBRATION)
        
        self.target_count = int(self.config.get_param("target_count"))
        self.pause = int(self.config.get_param("pause"))
        self.user_name = self.config.get_param("user_name")
        self.file_path =self.config.get_param("file_path")
        self.time_exp = int(self.config.get_param("time_exp"))

        self.ready()
        self.run()
        
    def run(self):
        self.logger.info("START Biofeedback Calibration...")
        config = biofeedback_calibration.biofeedback_calibration_run(self.target_count, self.pause, self.time_exp)
        self.logger.info("FINISH Biofeedback Calibration...")

        self._set_appconfig(self.file_path, self.user_name, config)

        acquisition_helper.send_finish_saving(self.conn)

        time.sleep(5)
        sys.exit(0)

    def _set_appconfig(self, path, name, config):
        config_file = acquisition_helper.get_file_path(path, name)+'.confapp'
        f = open(config_file, 'w')
        pickle.dump(config, f)
        f.close()

if __name__ == "__main__":
    BiofeedbackCalibration(settings.MULTIPLEXER_ADDRESSES).loop()
