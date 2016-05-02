#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Anna Chabuda <anna.chabuda@gmail.com>

import time, sys, pickle

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.configs import settings, variables_pb2
from obci.acquisition import acquisition_helper
from obci.interfaces.biofeedback.calibration import biofeedback_calibration

class BiofeedbackCalibration(ConfiguredMultiplexerServer):
	"""A class for creating a manifest file with metadata."""
	def __init__(self, addresses):
		super( BiofeedbackCalibration, self).__init__(addresses=addresses,
										  type=peers.LOGIC_P300_CALIBRATION)
		
		self.target_count = int(self.config.get_param("target_count"))
		self.user_name = self.config.get_param("user_name")
		self.file_path = self.config.get_param("file_path")

		self.ready()
		self.run()
		
	def run(self):
		self.logger.info("START Biofeedback Calibration...")
		biofeedback_calibration.biofeedback_calibration_run()
		self.logger.info("FINISH Biofeedback Calibration...")

		acquisition_helper.send_finish_saving(self.conn)

		time.sleep(5)
		sys.exit(0)

if __name__ == "__main__":
	BiofeedbackCalibration(settings.MULTIPLEXER_ADDRESSES).loop()
