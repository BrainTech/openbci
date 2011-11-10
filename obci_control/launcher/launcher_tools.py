#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys


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
	pythonpath=os.environ["PYTHONPATH"]
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