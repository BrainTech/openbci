#!/usr/bin/python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types

from peer.configured_client import ConfiguredClient
import time
import settings

class SaverControl(ConfiguredClient):

	def __init__(self, addresses, type):
		super(SaverControl, self).__init__(addresses, type)
		self.sleep_time_s = int(self.get_param('sleep_time_s'))
		print '[', self.config.peer_id, '] INITIALIZED!', self.sleep_time_s

	def run(self):
		print '[', self.config.peer_id, '] RUN!', self.sleep_time_s
		self.ready()
		print '[', self.config.peer_id, '] READY!', self.sleep_time_s
		time.sleep(self.sleep_time_s)
		self.conn.send_message(message='', type=types.SIGNAL_SAVER_FINISH_SAVING)

	def validate_params(self, params):
		try:
			int(self.get_param('sleep_time_s'))
		except Exception as e:
			print 'bleee', e


if __name__ == '__main__':
	SaverControl(settings.MULTIPLEXER_ADDRESSES, peers.ETR_SERVER).run()