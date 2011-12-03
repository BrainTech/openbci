#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys



NOT_READY = 'not_ready'
READY_TO_LAUNCH = 'ready_to_launch'
LAUNCHING = 'launching'
RUNNING = 'running'
FINISHED = 'finished'
CRASHED = 'crashed'
KILLED = 'killed'

EXP_STATUSES = [NOT_READY, READY_TO_LAUNCH, LAUNCHING, RUNNING, FINISHED, CRASHED, KILLED]

class ExperimentStatus(object):
	def __init__(self):
		self.status_name = NOT_READY
		self.details = {}
		self.peers_status = {}

	def set_status(self, status_name, details={}):
		self.status_name = status_name
		self.details = details

	def as_dict(self):
		d = dict(status_name=self.status_name,
				details=self.details, peers_status={})
		for peer_id, st in self.peers_status.iteritems():
			d['peers_status'][peer_id] = st.as_dict()
		return d

	def peer_status(self, peer_id):

		return self.peers_status.get(peer_id, None)


class PeerStatus(object):
	def __init__(self, peer_id):
		self.peer_id = peer_id
		self.status_name = NOT_READY
		self.details = {}

	def set_status(self, status_name, details=()):
		self.status_name = status_name
		self.details = details

	def as_dict(self):
		return dict(peer_id=self.peer_id, status_name=self.status_name,
				details=self.details)



def obci_root():
	path = os.path.realpath(os.path.dirname(__file__))
	path = os.path.split(path)[0]
	path = os.path.split(path)[0]
	return path

def obci_pythonpath():
	root = obci_root()
	obci_path = os.path.join(root, 'openbci')

	lib_python_dir = ''.join(['python', str(sys.version_info[0]), '.',
											str(sys.version_info[1])])
	mx_python_path = os.path.join(root, 'multiplexer-install', 'lib',
									lib_python_dir, 'site-packages')
	obci_control_path = os.path.join(root, 'obci_control')

	return os.pathsep.join([root, obci_path, mx_python_path, obci_control_path])

def update_obci_syspath():
	paths_str = obci_pythonpath()
	for direct in paths_str.split(os.pathsep):
		sys.path.insert(1, direct)

def update_pythonpath():
	obci_paths = obci_pythonpath()
	pythonpath=os.environ["PYTHONPATH"] if "PYTHONPATH" in os.environ else ''
	pythonpath=os.pathsep.join([pythonpath, obci_paths])
	os.environ["PYTHONPATH"] = pythonpath


def mx_path():
	return os.path.join(obci_root(), 'multiplexer-install', 'bin')



if __name__=='__main__':
	print obci_pythonpath()

# env = os.environ.copy()

# _env = {
#         "MULTIPLEXER_ADDRESSES": "0.0.0.0:31889",
#         "MULTIPLEXER_PASSWORD": "",
#         "MULTIPLEXER_RULES": os.path.join(home, 'multiplexer.rules'),
#         "PYTHONPATH": obci_path + ":" + obci_path + "../:"+ mx_python_path+":" + obci_path + "../obci_control/:"
# }
# print _env["PYTHONPATH"]
# env.update(_env)

# for x in env["PYTHONPATH"].split(":"):
#     sys.path.insert(1, x)