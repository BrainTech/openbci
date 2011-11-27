#!/usr/bin/python
# -*- coding: utf-8 -*-

# 1. przeczytać plik uruchomieniowy
#		-- ustawić ID modułów
# dla każdego modułu:
#		-- przeczytać pliki konf
#		-- sprawdzić&ustawić nazwy źródeł
# ustawić 'na sucho' źródła

import warnings
from common.config_helpers import *
import launcher_tools

class OBCIExperimentConfig(object):
	def __init__(self, launch_file_path=None, uuid=None, origin_machine=None):
		self.uuid = uuid
		self.launch_file_path = launch_file_path
		self.origin_machine = origin_machine if origin_machine else ''
		self.scenario_dir = ''
		self.mx = 1
		self.peers = {}

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

	def config_ready(self):

		for peer_state in self.peers.values():
			if not peer_state.ready():
				return False

		# check config graph

		return True

	def status(self, status_obj):
		ready = self.config_ready()
		st = launcher_tools.READY_TO_LAUNCH if ready else launcher_tools.NOT_READY

		status_obj.set_status(st)
		#TODO details, e.g. info about cycles

		for peer_id in self.peers:
			pst = status_obj.peers_status[peer_id] = launcher_tools.PeerStatus(peer_id)
			self.peers[peer_id].status(pst)

	def peer_machines(self):
		machines = set(self.origin_machine)
		for peer in self.peers.values():
			if peer.machine:
				machines.add(peer.machine)
		return list(machines)

	def check_dependency_cycles(self):
		#TODO
		pass

	def check_config_source_cycles(self):
		#TODO
		pass

	def info(self):
		exp = {}
		exp["uuid"] = self.uuid
		exp["origin_machine"] = self.origin_machine
		exp["launch_file_path"] = self.launch_file_path
		peers = {}
		for p in self.peers:
			peers[p] = self.peers[p].info()
		exp["peers"] = peers
		return exp




class PeerConfigDescription(object):
	def __init__(self, peer_id, experiment_id, config=None, path=None, machine=None):
		self.peer_id = peer_id

		self.experiment_id = experiment_id

		self.config = config
		self.path = path
		self.machine = machine

	def ready(self):
		ready = self.config is not None and \
				self.path is not None and\
				self.machine is not None and\
				self.peer_id is not None
		return ready and self.config.config_sources_ready() and\
				self.config.launch_deps_ready()

	def status(self, peer_status_obj):
		ready = self.ready()
		st = launcher_tools.READY_TO_LAUNCH if ready else launcher_tools.NOT_READY

		peer_status_obj.set_status(st)

	def info(self, detailed=False):
		info = dict(peer_id=self.peer_id,
					path=self.path, machine=self.machine,
					config_sources=None, launch_dependencies=None,
					local_params=None, ext_params=None)

		if not self.config:
			return info

		info[CONFIG_SOURCES] = self.config.config_sources
		info[LAUNCH_DEPENDENCIES] = self.config.launch_deps

		if detailed:
			info[LOCAL_PARAMS] = self.config.local_params
			info[EXT_PARAMS] = self.config.ext_param_defs
		return info



class OBCIPeerOSInfo(object):

	def __init__(self, peer_id, system_instance_id, machine=None):
		pass




class OBCISystemConfigError(Exception):
	pass


class OBCISystemConfigWarning(Warning):
	pass