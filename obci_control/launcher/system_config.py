#!/usr/bin/python
# -*- coding: utf-8 -*-


import warnings
from common.config_helpers import *
import launcher_tools
from peer.peer_config_serializer import PeerConfigSerializerCmd
import peer.peer_config_parser

class OBCIExperimentConfig(object):
	def __init__(self, launch_file_path=None, uuid=None, origin_machine=None):
		self.uuid = uuid
		self.launch_file_path = launch_file_path
		self.origin_machine = origin_machine if origin_machine else ''
		self.scenario_dir = ''
		self.mx = 0
		self.peers = {}

	def peer_config(self, peer_id):
		return self.peers[peer_id].config

	def update_local_param(self, peer_id, p_name, p_value):
		if peer_id not in self.peers:
			raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))
		return self.peers[peer_id].config.update_local_param(p_name, p_value)

	def update_external_param(self, peer_id, p_name, src, src_param):
		if peer_id not in self.peers:
			raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))
		return self.peers[peer_id].config.update_external_param_def(p_name, src+'.'+src_param)

	def update_peer_config(self, peer_id, config_dict):
		if peer_id not in self.peers:
			raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))
		conf = self.peers[peer_id].config
		dictparser = peer.peer_config_parser.parser('python')
		return dictparser.parse(config_dict, conf, update=True)

	def peer_path(self, peer_id):
		return self.peers[peer_id].path

	def peer_machine(self, peer_id):
		return self.peers[peer_id].machine

	def add_peer(self, peer_id):
		self.peers[peer_id] = PeerConfigDescription(peer_id, self.uuid)

	def set_peer_config(self, peer_id, peer_config):
		self.peers[peer_id].config = peer_config

	def set_peer_path(self, peer_id, path):
		self.peers[peer_id].path = path

	def set_config_source(self, peer_id, src_name, src_peer_id):
		if src_peer_id not in self.peers:
			raise OBCISystemConfigError("(src) Peer ID {0} not in peer list".format(src_peer_id))
		if peer_id not in self.peers:
			raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))
		if self.peers[peer_id] is None:
			raise OBCISystemConfigError("Configuration for peer ID {0} does not exist".format(peer_id))

		self.peers[peer_id].config.set_config_source(src_name, src_peer_id)

	def set_launch_dependency(self, peer_id, dep_name, dep_peer_id):
		if dep_peer_id not in self.peers:
			raise OBCISystemConfigError("(dep) Peer ID {0} not in peer list".format(dep_peer_id))
		if peer_id not in self.peers:
			raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))
		if self.peers[peer_id] is None:
			raise OBCISystemConfigError("Configuration for peer ID {0} does not exist".format(peer_id))

		self.peers[peer_id].config.set_launch_dependency(dep_name, dep_peer_id)

	def set_peer_machine(self, peer_id, machine_name):
		if peer_id not in self.peers:
			raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))

		self.peers[peer_id].machine = machine_name

	def all_param_values(self, peer_id):

		if peer_id not in self.peers:
			raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))

		config = self.peers[peer_id].config
		not_fresh = config.param_values
		vals = {}
		for key in not_fresh:
			vals[key] = self._param_value(peer_id, key, config)
		return vals
	
	def param_value(self, peer_id, param_name):
		if peer_id not in self.peers:
			raise OBCISystemConfigError("Peer ID {0} not in peer list".format(peer_id))

		config = self.peers[peer_id].config
		return self._param_value(peer_id, param_name, config)

	def _param_value(self, peer_id, param_name, config):
		if param_name in config.local_params:
			return config.local_params[param_name]
		elif param_name in config.external_param_defs:
			peer, param = config.external_param_defs[param_name]
			return self.param_value(peer, param)
		else:
			raise OBCISystemConfigError("Param {0} does not exist in {1}".format(param_name, peer_id))

	def config_ready(self):
		details = {}
		
		if not self.peers:	
			return False, details

		for peer_state in self.peers.values():
			if not peer_state.ready(details):
				return False, details

		# check config graph

		return True, {}

	def status(self, status_obj):
		ready, details = self.config_ready()
		st = launcher_tools.READY_TO_LAUNCH if ready else launcher_tools.NOT_READY

		status_obj.set_status(st, details=details)
		#TODO details, e.g. info about cycles

		for peer_id in self.peers:
			pst = status_obj.peers_status[peer_id] = launcher_tools.PeerStatus(peer_id)
			self.peers[peer_id].status(pst)

	def peer_machines(self):
		machines = set([self.origin_machine])
		for peer in self.peers.values():
			if peer.machine:
				machines.add(peer.machine)
		return list(machines)

	def launch_data(self, peer_machine):
		ldata = {}
		# if peer_machine == self.origin_machine and self.mx:
			# ldata['multiplexer'] = dict(machine=self.origin_machine,
			# 			peer_id='multiplexer', peer_type='obci_multiplexer',
			# 			path=launcher_tools.mx_path(), args=[])
		for peer in self.peers.values():
			machine = peer.machine if peer.machine else self.origin_machine
			if machine == peer_machine:
				ldata[peer.peer_id] = peer.launch_data()
		return ldata

	def check_dependency_cycles(self):
		#TODO
		pass

	def check_config_source_cycles(self):
		#TODO
		pass

	def peers_info(self):
		peers = {}
		for p in self.peers:
			peers[p] = self.peers[p].info()
		return peers

	def info(self):
		exp = {}
		exp["uuid"] = self.uuid
		exp["origin_machine"] = self.origin_machine
		exp["launch_file_path"] = self.launch_file_path
		peers = self.peers_info()
		exp["peers"] = peers
		return exp




class PeerConfigDescription(object):
	def __init__(self, peer_id, experiment_id, config=None, path=None, machine=None):
		self.peer_id = peer_id

		self.experiment_id = experiment_id

		self.config = config
		self.path = path
		self.machine = machine

	def ready(self, details=None):
		loc_det = {}
		ready = self.config is not None and \
				self.path is not None and\
				self.machine is not None and\
				self.peer_id is not None

		if not ready:
			return ready
		ready = self.config.config_sources_ready(loc_det) and ready
		ready = self.config.launch_deps_ready(loc_det) and ready
		if details is not None:
			details[self.peer_id] = loc_det
		return ready

	def status(self, peer_status_obj):
		det = {}
		ready = self.ready(det)
		st = launcher_tools.READY_TO_LAUNCH if ready else launcher_tools.NOT_READY

		peer_status_obj.set_status(st, details=det)

	def peer_type(self):
		if self.peer_id.startswith('mx'):
			return 'multiplexer'
		else:
			return 'obci_peer'

	def launch_data(self):
		ser = PeerConfigSerializerCmd()
		args = [self.peer_id]
		ser.serialize(self.config, args)

		return dict(peer_id=self.peer_id, experiment_id=self.experiment_id,
					path=self.path, machine=self.machine,
					args=args, peer_type=self.peer_type())


	def info(self, detailed=False):
		info = dict(peer_id=self.peer_id,
					path=self.path, machine=self.machine, peer_type=self.peer_type()
					)

		if not self.config:
			return info

		info[CONFIG_SOURCES] = self.config.config_sources
		info[LAUNCH_DEPENDENCIES] = self.config.launch_deps

		if detailed:
			info[LOCAL_PARAMS] = self.config.local_params
			info[EXT_PARAMS] = self.config.ext_param_defs
		return info



class OBCISystemConfigError(Exception):
	pass


class OBCISystemConfigWarning(Warning):
	pass