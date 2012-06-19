#!/usr/bin/python
# -*- coding: utf-8 -*-
import time

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_client import ConfiguredClient

from configs import settings, variables_pb2

class SaverControl(ConfiguredClient):

	def __init__(self, addresses):
		super(SaverControl, self).__init__(addresses=addresses, type=peers.SIGNAL_SAVER_CONTROL)
		self.sleep_time_s = int(self.get_param('sleep_time_s'))
		print '[', self.config.peer_id, '] INITIALIZED!', self.sleep_time_s

	def run(self):
		print '[', self.config.peer_id, '] RUN!', self.sleep_time_s
		self.ready()
		print '[', self.config.peer_id, '] READY!', self.sleep_time_s
		time.sleep(self.sleep_time_s)
		v = variables_pb2.Variable()
		v.key = 'finish'
		v.value = ''
		print '[', self.config.peer_id, '] SEND CONTROL!'

		self.conn.send_message(message=v.SerializeToString(), 
				       type=types.SIGNAL_SAVER_CONTROL_MESSAGE,
				       flush=True)
		time.sleep(5)

	def validate_params(self, params):
		try:
			int(self.get_param('sleep_time_s'))
		except Exception as e:
			print 'bleee', e


if __name__ == '__main__':
	SaverControl(settings.MULTIPLEXER_ADDRESSES).run()
