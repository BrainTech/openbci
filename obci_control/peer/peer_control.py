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
WAIT_READY_SIGNAL = "wait_ready_signal"
CONFIG_FILE = "config_file"
PEER_ID = "peer_id"

class PeerControl(object):

	def __init__(self, p_peer=None, param_validate_method=None,
							   param_change_method=None):
		self.core = peer_config.PeerConfig()
		self.peer = p_peer
		self.peer_validate_params = param_validate_method
		self.peer_params_changed = param_change_method

		self.wait_ready_signal = False
		self.peer_id = None

		self.cmd_overrides = {}
		self.file_list = []


	def initialize_config(self, connection):
		# parse command line
		self.process_command_line()

		# parse default config file
		self.load_config_base()

		# parse other config files (names from command line)
		for filename in self.file_list:
			self._load_config_from_file(filename, CONFIG_FILE_EXT, update=True)

		# parse overrides (from command line)
		dictparser = peer_config_parser.parser('python')
		dictparser.parse(self.cmd_overrides, self.core, update=True)

		self.register_config(connection)
		self.request_ext_params(connection)
		self.peer_validate_params(self.core.param_values)


	def process_command_line(self):
		cmd_ovr, other_params = PeerCmd().parse_cmd()
		self.peer_id = self.core.peer_id = other_params[PEER_ID]
		if other_params[CONFIG_FILE] is not None:
			self.file_list = other_params[CONFIG_FILE]
		self.cmd_overrides = cmd_ovr
		if other_params[WAIT_READY_SIGNAL]:
			self.wait_ready_signal = True


	def load_config_base(self):
		"""Parse the base configuration file, named the same as peer's
		implementation file"""

		if self.peer is None:
			raise NoPeerError

		peer_file = inspect.getfile(self.peer.__init__)
		base_name = peer_file.rsplit('.', 1)[0]
		base_config_path = '.'.join([base_name, CONFIG_FILE_EXT])
		print "Peer {0} base config path: {1}".format(self.peer_id, base_config_path)

		self._load_config_from_file(base_config_path, CONFIG_FILE_EXT)
		print "Peer {0} base config: {1}".format(self.peer_id, self.core)


	def _load_config_from_file(self, p_path, p_type, update=False):
		with open(p_path) as f:
			parser = peer_config_parser.parser(p_type)
			parser.parse(f, self.core)


	def handle_config_message(self, mxmsg):

		if mxmsg.type in cmsg.MX_CFG_MESSAGES:
			message = cmsg.unpack_msg(mxmsg.type, mxmsg.message)

			msg, mtype = self._call_handler(mxmsg.type, message)
			if msg is None:
				self.peer.no_response()
			else:
				msg = cmsg.pack_msg(msg)
				self.peer.send_message(message=msg, type=mtype, to=int(mxmsg.from_), flush=True)

	def _call_handler(self, mtype, message):
		if mtype == types.PARAMS_CHANGED:
			return self.handle_params_changed(message)
		elif mtype == types.PEER_READY_SIGNAL:
			return self.handle_peer_ready_signal(message)
		elif mtype == types.SHUTDOWN_REQUEST:
			self.peer.shut_down()
			#return None, None
		else:
			return None, None

	def handle_params_changed(self, p_msg):
		print "peer_control: PARAMS CHANGED - ", p_msg.sender
		params = cmsg.params2dict(p_msg)
		param_owner = p_msg.sender

		old_values = {}
		updated = {}
		if param_owner in self.core.config_sources:
			src_params = self.core.params_for_source(src_name)

			for par_name in [par for par in params if par in src_params]:
				old = self.core.get_param(par_name)
				new = params[par_name]
				if old != params[par_name]:
					old_values[par_name] = old
					updated[par_name] = new
					self.core.set_param_from_source(reply_msg.sender, par_name, new)
			if not self.peer_params_changed(updated):
				#restore...
				for par, val in old_values.iteritems():
					self.core.set_param_from_source(reply_msg.sender, par, val)

		if param_owner == self.peer_id:
			local_params = self.core.local_params
			for par, val in params.iteritems():
				if par not in local_params:
					## protest?
					continue
				if val != self.core.get_param(par):
					old_values[par] = self.core.get_param(par)
					updated[par] = val
					self.core.update_local_param(par, val)
			if not self.peer_params_changed(updated):
				for par, val in old_values.iteritems():
					self.core.update_local_param(par, val)

		return None, None

	def config_ready(self):
		return self.core.config_ready() and self.peer_id is not None

	def handle_peer_ready_signal(self, p_msg):
		if not self.peer.ready_to_work and self.config_ready():
			self.peer.ready_to_work = True
			self.send_peer_ready(self.peer.conn)
			return None, None
		else:
			return cmsg.fill_msg(types.CONFIG_ERROR), types.CONFIG_ERROR


	def get_param(self, p_name):
		return self.core.get_param(p_name)

	def set_param(self, p_name, p_value):
		#TODO let know other peers...
		# right now it's best not to use this method
		return self.core.update_local_param(p_name, p_value)


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
					reply_msg = cmsg.unpack_msg(reply.type, reply.message)
					params = cmsg.params2dict(reply_msg)

					for par, val in params.iteritems():
						self.core.set_param_from_source(reply_msg.sender, par, val)
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

		ready = False
		while not ready:
			reply = self.__query(connection, msg, types.PEERS_READY_QUERY)

			if reply is None:
				#TODO sth bad happened, raise exception?
				continue
			if reply.type is types.READY_STATUS:
				ready = cmsg.unpack_msg(reply.type, reply.message).peers_ready
			if not ready:
				time.sleep(0.2)
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