#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
from obci.control.peer.configured_client import ConfiguredClient
from obci.acquisition import acquisition_helper
from obci.configs import settings, variables_pb2
from multiplexer.multiplexer_constants import peers, types

class SaverControl(ConfiguredClient):
	def __init__(self, addresses):
		super(SaverControl, self).__init__(addresses=addresses, type=peers.CLIENT)
		self.sleep_time_s = int(self.get_param('acquisition_time_s'))
		self.logger.info(''.join(['[', str(self.config.peer_id), '] INITIALIZED!', str(self.sleep_time_s)]))
		self.ready()

	def run(self):
		time.sleep(self.sleep_time_s)
	        self.logger.info(''.join(['[', str(self.config.peer_id), '] SEND CONTROL!']))
		self.logger.info("T-before: "+repr(time.time()))
		acquisition_helper.finish_saving()
		self.logger.info("T-after: "+repr(time.time()))

if __name__ == '__main__':
	SaverControl(settings.MULTIPLEXER_ADDRESSES).run()
