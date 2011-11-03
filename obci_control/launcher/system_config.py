#!/usr/bin/python
# -*- coding: utf-8 -*-

# 1. przeczytać plik uruchomieniowy
#		-- ustawić ID modułów
# dla każdego modułu:
#		-- przeczytać pliki konf
#		-- sprawdzić&ustawić nazwy źródeł
# ustawić 'na sucho' źródła

import warnings

class OBCISystemConfig(object):
	def __init__(self, launch_file_path=None, uuid=None, origin_machine=None):
		self.uuid = uuid
		self.launch_file_path = uuid
		self.origin_machine = uuid

		self.peers = {}

	def add_peer(self, peer_id):
		self.peers[peer_id] = OBCIPeerState(peer_id, self.uuid)

	def set_peer_config(self, peer_id, peer_config):
		self.peers[peer_id].config = peer_config

	def set_peer_path(self, peer_id, path):
		self.peers[peer_id].path = path

	def set_config_source(self, peer_id, src_name, src_peer_id):
		if src_peer_id not in self.peers.keys() or \
			peer_id not in self.peers.keys() or \
			self.peers[peer_id] is None:
			raise OBCISystemConfigError()

		self.peers[peer_id].config.set_config_source(src_name, src_peer_id)

	def config_ready(self):

		for peer_state in self.peers.values():
			if not peer_state.config.config_ready():
				return False

		# check config graph

		return True



NOT_RUNNING = 0
LAUNCHING = 1
RUNNING = 2
FINISHED = 3
FAILED = 4

PEER_STATES = [NOT_RUNNING, LAUNCHING, RUNNING, FINISHED, FAILED]

class OBCIPeerState(object):
	def __init__(self, peer_id, system_instance_id, config=None, path=None, machine=None):
		self.peer_id = peer_id
		self.uuid = None

		self.system_instance_id = system_instance_id

		self.config = config
		self.path = path
		self.machine = machine

		self.state = NOT_RUNNING

		self.os_info = None


class OBCIPeerOSInfo(object):

	def __init__(self, peer_id, system_instance_id, machine=None):
		pass




class OBCISystemConfigError(Exception):
	pass


class OBCISystemConfigWarning(Warning):
	pass