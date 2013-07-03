#!/usr/bin/python
# -*- coding: utf-8 -*-

#import system_settings

import os
import os.path
import shutil
from obci.control.peer.config_defaults import CONFIG_DEFAULTS


OBCI_CONTROL_LOG_DIR = os.path.join(CONFIG_DEFAULTS["log_dir"], "control")


USE_ZMQ = False

PORT_RANGE = (30000, 60000)

OBCI_HOME_DIR = os.path.join(os.path.expanduser('~'), '.obci')
DEFAULT_SANDBOX_DIR = os.path.join(OBCI_HOME_DIR, 'sandbox')
DEFAULT_SCENARIO_DIR = os.path.join(OBCI_HOME_DIR, 'scenarios')

SERVER_CONTACT_NAME = '.obci_server_contact'
MAIN_CONFIG_NAME = 'main_config.ini'

def __obci_install_dir():
    dirname = os.path.abspath(os.path.dirname(__file__))
    test_suffix = os.path.join('control', 'common')
    if dirname.endswith(test_suffix):
        return dirname[:-len(test_suffix)]
    else:
        # TODO: better raise an exception
        return None

INSTALL_DIR = __obci_install_dir()

__template_dir = os.path.join(INSTALL_DIR, 'control', 'templates')
MAIN_CONFIG_TEMPLATE_PATH = os.path.join(__template_dir, MAIN_CONFIG_NAME)

if not os.path.exists(OBCI_HOME_DIR):
    os.makedirs(OBCI_HOME_DIR)
if not os.path.exists(DEFAULT_SANDBOX_DIR):
    os.mkdir(DEFAULT_SANDBOX_DIR)
if not os.path.exists(DEFAULT_SCENARIO_DIR):
    os.mkdir(DEFAULT_SCENARIO_DIR)
if not os.path.exists(os.path.join(OBCI_HOME_DIR, MAIN_CONFIG_NAME)):
    shutil.copyfile(MAIN_CONFIG_TEMPLATE_PATH, os.path.join(OBCI_HOME_DIR, MAIN_CONFIG_NAME))

