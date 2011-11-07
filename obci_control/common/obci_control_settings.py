#!/usr/bin/python
# -*- coding: utf-8 -*-

#import system_settings

import os.path

USE_ZMQ = False

PORT_RANGE = (30000, 60000)

DEFAULT_SANDBOX_DIR = '~/.obci'

def obci_install_dir():
	f = __file__
	dirname = os.path.dirname(f)
	if dirname.endswith('obci_control/common'):
		ind = dirname.rfind('obci_control/common')
		return f[:ind]
	else: return None

INSTALL_DIR = obci_install_dir()