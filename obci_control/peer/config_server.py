#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zmq

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client
from peer.peer_cmd import PeerCmd
from configs import settings


import common.config_message as cmsg
from launcher.launcher_messages import message_templates
from common.message import OBCIMessageTool, send_msg, recv_msg


class ConfigServer(BaseMultiplexerServer):

	def __init__(self, addresses):
		self._configs = {}
		self._ready_peers = []
		self.__to_all = False
		self.spare_conn = connect_client(addresses=addresses, type=peers.CONFIGURER)
		self.mtool = OBCIMessageTool(message_templates)
		self.launcher_sock = None
		params, other_params = PeerCmd().parse_cmd()
		print '[config_server]', params, other_params
		addr = params['local_params'].get('launcher_socket_addr', '')
		if addr != '':
			self.ctx = zmq.Context()
			self.launcher_sock = self.ctx.socket(zmq.PUB)
			try:
				self.launcher_sock.connect(addr)
			except Exception, e:
				print "[config_server] -- failed to connect to address", addr, "!!!"
				self.launcher_sock = None
			else:
				print "[config_server] OK OK OK OK OK OK", addr
		super(ConfigServer, self).__init__(addresses=addresses, type=peers.CONFIG_SERVER)


	def handle_message(self, mxmsg):
		message = cmsg.unpack_msg(mxmsg.type, mxmsg.message)

		msg, mtype, launcher_msg = self._call_handler(mxmsg.type, message)
		#print mxmsg.type, mtype
		if msg is None:
			self.no_response()
		else:
			msg = cmsg.pack_msg(msg)
			if self.__to_all:
				self.no_response()
				self.spare_conn.send_message(message=msg, type=mtype, flush=True)
				self.__to_all = False
			else:
				self.send_message(message=msg, to=int(mxmsg.from_), type=mtype, flush=True)
		if launcher_msg is not None and self.launcher_sock is not None:
			print '[config_server]  SENDING msg ', launcher_msg[:40] + '[...]'
			send_msg(self.launcher_sock, launcher_msg)

	def _call_handler(self, mtype, message):
		if mtype == types.GET_CONFIG_PARAMS:
			return self.handle_get_config_params(message)
		elif mtype == types.REGISTER_PEER_CONFIG:
			return self.handle_register_peer_config(message)
		elif mtype == types.UNREGISTER_PEER_CONFIG:
			return self.handle_unregister_peer_config(message)
		elif mtype == types.UPDATE_PARAMS:
			msg, mtype, launcher_msg =  self.handle_update_params(message)
			if mtype != types.CONFIG_ERROR:
				self.__to_all = True
			return msg, mtype, launcher_msg
		elif mtype == types.PEER_READY:
			return self.handle_peer_ready(message)
		elif mtype == types.PEERS_READY_QUERY:
			return self.handle_peers_ready_query(message)
		else:
			return None, None, None

	def handle_get_config_params(self, message_obj):
		param_owner = message_obj.receiver
		names = message_obj.param_names
		if param_owner not in self._configs:
			return cmsg.fill_msg(types.CONFIG_ERROR), types.CONFIG_ERROR, None

		#TODO error when param_name does not exist?
		params = {}
		for name in names:
			if name in self._configs[param_owner]:
				params[name] = self._configs[param_owner][name]

		mtype = types.CONFIG_PARAMS
		msg = cmsg.fill_msg(mtype, sender=param_owner)
		cmsg.dict2params(params, msg)
		return msg, mtype, None

	def handle_register_peer_config(self, message_obj):
		params = cmsg.params2dict(message_obj)
		peer_id = message_obj.sender

		if peer_id in self._configs:
			mtype = types.CONFIG_ERROR
			msg = cmsg.fill_msg(mtype)
		else:
			self._configs[peer_id] = params
			mtype = types.PEER_REGISTERED
			msg = cmsg.fill_msg(mtype, peer_id=peer_id)
			launcher_msg = self.mtool.fill_msg('obci_peer_registered',
											peer_id=peer_id, params=params)
		return msg, mtype, launcher_msg


	def handle_unregister_peer_config(self, message_obj):
		self._configs.pop(message_obj.peer_id)

		if message_obj.peer_id in self._ready_peers:
			self._ready_peers.remove(message_obj.peer_id)
		return None, None, None #TODO confirm unregister...

	def handle_update_params(self, message_obj):
		params = cmsg.params2dict(message_obj)
		param_owner = message_obj.sender
		if param_owner not in self._configs:
			launcher_msg = None
			return cmsg.fill_msg(types.CONFIG_ERROR,
								error_str="Peer unknown: {0}".format(param_owner)),\
					types.CONFIG_ERROR,\
					launcher_msg
		updated = {}
		for param in params:
			if param in self._configs[param_owner]:
				self._configs[param_owner][param] = params[param]
				updated[param] = params[param]

		if updated:
			mtype = types.PARAMS_CHANGED
			msg = cmsg.fill_msg(types.PARAMS_CHANGED, sender=param_owner)
			cmsg.dict2params(updated, msg)
			launcher_msg = self.mtool.fill_msg('obci_peer_params_changed',
										peer_id=param_owner, params=updated)
			return msg, mtype, launcher_msg
		return None, None, None

	def handle_peer_ready(self, message_obj):
		peer_id = message_obj.peer_id
		if peer_id not in self._configs:
			return cmsg.fill_msg(types.CONFIG_ERROR), types.CONFIG_ERROR, None
		self._ready_peers.append(peer_id)
		launcher_msg = self.mtool.fill_msg('obci_peer_ready', peer_id=peer_id)
		return message_obj, types.PEER_READY, launcher_msg

	def handle_peers_ready_query(self, message_obj):

		peer_id = message_obj.sender
		if peer_id not in self._configs:
			return cmsg.fill_msg(types.CONFIG_ERROR), types.CONFIG_ERROR, None

		green_light = True
		for dep in message_obj.deps:
			if not dep in self._ready_peers:
				green_light = False

		return cmsg.fill_msg(types.READY_STATUS,
							receiver=peer_id, peers_ready=green_light), types.READY_STATUS, None



if __name__ == "__main__":

	ConfigServer(settings.MULTIPLEXER_ADDRESSES).loop()

#TODO make doctests from this
"""
	srv = ConfigServer(settings.MULTIPLEXER_ADDRESSES)
	print "REGISTRATION"
	reg = cmsg.fill_msg(types.REGISTER_PEER_CONFIG, sender="ja", receiver="")

	cmsg.dict2params(dict(wr=1, dfg=[1,2,3,4,'zuzanna']), reg)
	srv.handle_register_peer_config(reg)

	reg = cmsg.fill_msg(types.REGISTER_PEER_CONFIG, sender="ty", receiver="")
	cmsg.dict2params(dict(a=1, bb=['ssdfsdf', 'LOL']), reg)
	srv.handle_register_peer_config(reg)

	reg = cmsg.fill_msg(types.REGISTER_PEER_CONFIG, sender="on", receiver="")
	cmsg.dict2params(dict(lll=0), reg)
	srv.handle_register_peer_config(reg)

	print srv._configs

	print "PEER_READY"
	rdy = cmsg.fill_msg(types.PEER_READY, peer_id="on")
	srv.handle_peer_ready(rdy)
	rdy = cmsg.fill_msg(types.PEER_READY, peer_id="ja")
	srv.handle_peer_ready(rdy)
	print srv._ready_peers

	print "PEERS_READY_QUERY"
	rdq = cmsg.fill_msg(types.PEERS_READY_QUERY, sender="ja", deps=["on, ty"])
	print srv.handle_peers_ready_query(rdq)[0]
	rdq = cmsg.fill_msg(types.PEERS_READY_QUERY, sender="ty", deps=["on"])
	print srv.handle_peers_ready_query(rdq)[0]

	print "GET_CONFIG_PARAMS"
	par = cmsg.fill_msg(types.GET_CONFIG_PARAMS, sender="ja", receiver="ty", param_names=['a','b'])
	print srv.handle_get_config_params(par)[0]
	par = cmsg.fill_msg(types.GET_CONFIG_PARAMS, sender="ja", receiver="ty", param_names=['bb'])
	rep = srv.handle_get_config_params(par)[0]
	print rep, "decoded params:\n", cmsg.params2dict(rep)

	print "DEREGISTRATION"
	unr = cmsg.fill_msg(types.UNREGISTER_PEER_CONFIG, peer_id="ja")
	srv.handle_unregister_peer_config(unr)
	print srv._configs
"""
