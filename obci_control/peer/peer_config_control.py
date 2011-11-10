#!/usr/bin/python
# -*- coding: utf-8 -*-

import warnings
import time
import inspect

import peer_config
import peer_config_parser
from peer_cmd import PeerCmd

import common.config_message as cmsg

import settings
from multiplexer.multiplexer_constants import peers, types
from azouk._allinone import OperationFailed, OperationTimedOut

CONFIG_FILE_EXT = 'ini'
WAIT_CONFIG = "wait_config"
CONFIG_FILE = "config_file"
PEER_ID = "peer_id"

class PeerControl(object):

	def __init__(self, p_peer=None, param_processing_method=None,
							   param_change_trigger_method=None):
		self.core = peer_config.PeerConfig()
		self.peer = p_peer
		self.peer_process_param = param_processing_method
		self.peer_param_trigger = param_change_trigger_method

		self.cmd_overrides = {}
		self.file_list = []
		self.wait_config = False

		self.peer_id = None


	def initialize_config(self, connection):
		# parse command line
		self.process_cmd()

		# parse default config file
		self.load_config_base()

		# parse other config files (names from command line)
		for filename in self.file_list:
			self._load_config_from_file(filename, CONFIG_FILE_EXT, update=True)

		# parse overrides (from command line)
		dictparser = peer_config_parser.parser('python')
		dictparser.parse(self.cmd_overrides, self.core, update=True)

		# request external parameters
		# this will hang forever if there are cycles in the config depenency graph!
		self.request_ext_params(connection)
		self.register_config(connection)




	def process_cmd(self):
		cmd_ovr, other_params = PeerCmd().parse_cmd()
		self.peer_id = self.core.peer_id = other_params[PEER_ID]
		if other_params[CONFIG_FILE] is not None:
			self.file_list = other_params[CONFIG_FILE]
		self.cmd_overrides = cmd_ovr
		if other_params[WAIT_CONFIG]:
			self.wait_config = True


	def load_config_base(self):
		if self.peer is None:
			raise NoPeerError

		peer_file = inspect.getfile(self.peer.__init__)
		base_name = peer_file.rsplit('.', 1)[0]
		base_config_path = '.'.join([base_name, CONFIG_FILE_EXT])
		print base_config_path

		self._load_config_from_file(base_config_path, CONFIG_FILE_EXT)
		print "********************"
		print self.core


	def _load_config_from_file(self, p_path, p_type, update=False):
		with open(p_path) as f:
			parser = peer_config_parser.parser(p_type)
			parser.parse(f, self.core)


	def handle_config_message(self, p_type, p_msg):
		#TODO...
		return self._handle_unsupported_message(p_msg)



	def get_param(self, p_name):
		return self.core.get_param(p_name)

	def set_param(self, p_name, p_value):
		#TODO let know other peers...
		# right now it's best not to use this method
		return self.core.update_local_param(p_name, p_value)


	def _handle_set_config(self, p_msg):
		#jsonparser = peer_config_parser.parser('json')
		#jsonparser.parse(io.BytesIO(p_msg.message), self.core, update=True)
		pass


	def _handle_param_values(self, p_msg):
		params = cmsg.params2dict(p_msg)

		for par, val in params.iteritems():
			self.core.set_param_from_source(p_msg.sender, par, val)

	def _handle_unsupported_message(self, p_msg):
		warnings.warn(UnsupportedMessageType())
		return None

	def register_config(self, connection):
		if self.peer is None:
			raise NoPeerError

		msg = cmsg.fill_msg(types.REGISTER_PEER_CONFIG, sender=self.peer_id)

		params = self.core.local_params
		cmsg.dict2params(params, msg)

		connection.send_message(message=msg, type=types.REGISTER_PEER_CONFIG)


	def request_ext_params(self, connection):
		#TODO set timeout and retry count
		if self.peer is None:
			raise NoPeerError

		def _unset_param_count():
			return reduce(lambda x, y: x + y,
							[len(self.core.unset_params_for_source(src)) \
								for src in self.core.used_config_sources()], 0)

		while not self.core.config_ready():
			for src in self.core.used_config_sources():
				params = self.core.unset_params_for_source(src).keys()

				msg = cmsg.fill_msg(types.GET_CONFIG_PARAMS,
									sender=self.peer_id,
									param_names=params,
									receiver=self.core.config_sources[src])

				print "requesting: {0}".format(msg)
				reply = self.__query(connection, cmsg.pack_msg(msg),
									types.GET_CONFIG_PARAMS)

				if reply == None:
					# raise something?
					continue

				if reply.type == types.CONFIG_ERROR:
					print "peer {0} has not yet started".format(msg.receiver)
				elif reply.type == types.CONFIG_PARAMS:
					self._handle_param_values(cmsg.unpack_msg(reply.type, reply.message))
				else:
					print "WTF? {0}".format(reply.message)

			print "{0} external params still unset".format(_unset_param_count())
			time.sleep(0.1)

		print "External parameters initialised."
		print self.core

	def send_peer_ready(self, connection):
		if self.peer is None:
			raise NoPeerError
		mtype = types.PEER_READY
		connection.send_message(message=cmsg.fill_and_pack(mtype,
															peer_id=self.peer_id), type=mtype)


	def synchronize_ready(self, connection):
		#TODO set timeout and retry count
		if self.peer is None:
			raise NoPeerError

		others = self.core.launch_deps.values()
		msg = cmsg.fill_and_pack(types.PEERS_READY_QUERY, sender=self.peer_id,
															deps=others)
		reply = self.__query(connection, msg, types.PEERS_READY_QUERY)
		ready = False
		while not ready:
			time.sleep(0.2)
			if reply is None:
				#TODO sth bad happened, raise exception?
				continue
			if reply.type is types.READY_STATUS:
				ready = cmsg.unpack_msg(reply.type, reply.message).peers_ready
		print "Dependencies are ready, I can start working"




	def __query(self, conn, msg, msgtype):
		try:
			reply = conn.query(message=msg,
									type=msgtype)
		except OperationFailed:
			print "Could not connect"
			reply = None
		except OperationTimedOut:
			print "Operation timed out!"
			reply = None
		return reply




#todo message verification


class PeerConfigControlError(Exception):
	def __init__(self, value=None):
		self.value = value

	def __str__(self):
		if self.value is not None:
			return repr(self.value)
		else:
			return repr(self)

class NoPeerError(PeerConfigControlError):
	pass

class PeerConfigControlWarning(Warning):
	pass

class UnsupportedMessageType(PeerConfigControlWarning):
	pass