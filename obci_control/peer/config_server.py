#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings

from common.config_message import msg_for_type, unpack_msg, fill_msg, val2str, str2val


class ConfigServer(BaseMultiplexerServer):

	def __init__(self, addresses):
		self._configs = {}
		super(ConfigServer, self).__init__(addresses=addresses, type=peers.CONFIG_SERVER)


	def handle_message(self, mxmsg):
		message = unpack_msg(mxmsg.type, mxmsg.message)

		if mxmsg.type == types.GET_CONFIG_PARAMS:
			self.handle_get_config_params(message)
		elif mxmsg.type == types.REGISTER_PEER_CONFIG:
			self.handle_register_peer_config(message)
		elif mxmsg.type == types.UPDATE_PARAMS:
			self.handle_update_params(message)
		elif mxmsg.type == types.PEER_READY:
			self.handle_peer_ready(message)
		elif mxmsg.type == types.PEER_READY_QUERY:
			self.handle_peer_ready_query(message)
		else:
			self.no_response()


	def handle_get_config_params(self, message_obj):
		pass

	def handle_register_peer_config(self, message_obj):
		pass

	def handle_update_params(self, message_obj):
		pass

	def handle_peer_ready(self, message_obj):
		pass

	def handle_peer_ready_query(self, message_obj):
		pass

	def _register_peer_config(self, peer_id, peer_params):
		if peer_id in self._configs:
			raise PeerAlreadyRegistered()

		self._configs[peer_id] = peer_params


	def _get_param(self, peer_id, param_name):
		if peer_id not in self._configs:
			raise UnknownPeerID()
		if param_name not in self._configs[peer_id]:
			raise UnknownParamName()

		return self._configs[peer_id][param_name]



if __name__ == "__main__":
	ConfigServer(settings.MULTIPLEXER_ADDRESSES).loop()