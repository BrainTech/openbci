#!/usr/bin/python
# -*- coding: utf-8 -*-

#import system_settings

import os
import os.path

USE_ZMQ = False

PORT_RANGE = (30000, 60000)

OBCI_HOME_DIR = os.path.join(os.getenv('HOME'), '.obci')
DEFAULT_SANDBOX_DIR = os.path.join(OBCI_HOME_DIR, 'sandbox')

SERVER_CONTACT_NAME = '.obci_server_contact'
MAIN_CONFIG_NAME = 'main_config.ini'

def __obci_install_dir():
	f = __file__
	dirname = os.path.dirname(f)
	if dirname.endswith('obci_control/common'):
		ind = dirname.rfind('obci_control/common')
		return f[:ind]
	else: return None

INSTALL_DIR = __obci_install_dir()