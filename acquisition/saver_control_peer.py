#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
from obci_control.peer.configured_client import ConfiguredClient
from acquisition import acquisition_helper
from obci_configs import settings, variables_pb2
from multiplexer.multiplexer_constants import peers, types

from acquisition import acquisition_logging as logger
LOGGER = logger.get_logger("saver_control_peer", 'info')


class SaverControl(ConfiguredClient):
	def __init__(self, addresses):
		super(SaverControl, self).__init__(addresses=addresses, type=peers.CLIENT)
		self.sleep_time_s = int(self.get_param('acquisition_time_s'))
		LOGGER.info(''.join(['[', str(self.config.peer_id), '] INITIALIZED!', str(self.sleep_time_s)]))
		self.ready()

	def run(self):
		time.sleep(self.sleep_time_s)
	        LOGGER.info(''.join(['[', str(self.config.peer_id), '] SEND CONTROL!']))
		LOGGER.info("T-before: "+repr(time.time()))
		acquisition_helper.finish_saving()
		LOGGER.info("T-after: "+repr(time.time()))

if __name__ == '__main__':
	SaverControl(settings.MULTIPLEXER_ADDRESSES).run()
