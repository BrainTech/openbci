#!/usr/bin/python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2

from peer.peer_control import PeerControl
import common.config_message as cmsg

class ConfiguredMultiplexerServer(BaseMultiplexerServer):
	def __init__(self, addresses, type = None):
		super(ConfiguredMultiplexerServer, self).__init__(addresses, type)

		self.config = PeerControl(self,
									param_validate_method=self.validate_params,
									param_change_method=self.params_changed)
		self.ready_to_work = False

	def configure(self):
		self.init_config()
		self.send_peer_ready()
		self.synchronize_ready()

	def init_config(self):
		self.config.initialize_config(self.conn)

	def send_peer_ready(self):
		self.ready_to_work = True
		self.config.send_peer_ready(self.conn)

	def synchronize_ready(self):
		self.config.synchronize_ready(self.conn)


	def filter_config_message(self, mxmsg):
		print "Handling secret message!", mxmsg.type
		if mxmsg.type in cmsg.MX_CFG_MESSAGES:
			self.config.handle_config_message(mxmsg)

	def validate_params(self, params):
		print "VALIDATE PARAMS, {0}".format(params)
		return True

	def params_changed(self, params):
		print "PARAMS CHAnGED, {0}".format(params)
		return True

	def clean_up(self):
		print "CLEAN UP"
		pass

	def shut_down(self):
		self.clean_up()
		sys.exit(0)
