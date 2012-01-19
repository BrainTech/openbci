#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2

from peer.peer_control import PeerControl
import common.config_message as cmsg

class ConfiguredMultiplexerServer(BaseMultiplexerServer):
	def __init__(self, addresses, type = None):
		super(ConfiguredMultiplexerServer, self).__init__(addresses, type)

		self.ready_to_work = False
		self.config = PeerControl(self)
		self.config.connection = self.conn
		self.config.peer_validate_params = self.validate_params
		self.config.peer_params_change = self.params_changed
		result, details = self.config.initialize_config(self.conn)


		if not result:
			txt = '[{0}] (CRITICAL!) config initialisation FAILED: {1}'.format(
														self.config.peer_id, details)
			sys.exit(txt)
		else:
			self.validate_params(self.config.param_values())



	def ready(self):
		self.ready_to_work = True
		self.config.register_config(self.conn)
		self.config.send_peer_ready(self.conn)

	def param(self, param_name):
		return self.config.get_param(param_name)

	def set_param(self, param_name, param_value):
		self.config.set_param(param_name, param_value)

	def _is_private_message(self, mxmsg):
		return mxmsg.type in cmsg.MX_CFG_MESSAGES

	def _handle_message(self, mxmsg):
		print "Handling secret message!", mxmsg.type
		self.config.handle_config_message(mxmsg)

	def validate_params(self, params):
		print '[',self.config.peer_id,"] *VALIDATE PARAMS, {0}".format(params)
		return True

	def params_changed(self, params):
		print '[',self.config.peer_id,"] PARAMS CHAnGED, {0}".format(params)
		return True

	def clean_up(self):
		print '[',self.config.peer_id,"] CLEAN UP"

	def shut_down(self):
		self.clean_up()
		sys.exit(0)