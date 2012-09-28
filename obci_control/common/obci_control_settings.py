#!/usr/bin/python
# -*- coding: utf-8 -*-

#import system_settings

import os
import os.path
import shutil
from peer.config_defaults import CONFIG_DEFAULTS

OBCI_CONTROL_LOG_DIR = os.path.join(CONFIG_DEFAULTS["log_dir"], "obci_control")


USE_ZMQ = False

PORT_RANGE = (30000, 60000)

OBCI_HOME_DIR = os.path.join(os.getenv('HOME'), '.obci')
DEFAULT_SANDBOX_DIR = os.path.join(OBCI_HOME_DIR, 'sandbox')
DEFAULT_SCENARIO_DIR = os.path.join(OBCI_HOME_DIR, 'scenarios')

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

__template_dir = os.path.join(INSTALL_DIR, 'obci_control', 'templates')
MAIN_CONFIG_TEMPLATE_PATH = os.path.join(__template_dir, MAIN_CONFIG_NAME)

if not os.path.exists(OBCI_HOME_DIR):
    os.makedirs(OBCI_HOME_DIR)
    os.mkdir(DEFAULT_SANDBOX_DIR)
    os.mkdir(DEFAULT_SCENARIO_DIR)
    shutil.copyfile(MAIN_CONFIG_TEMPLATE_PATH, os.path.join(OBCI_HOME_DIR, MAIN_CONFIG_NAME))


