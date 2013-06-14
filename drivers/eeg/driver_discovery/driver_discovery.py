#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
#from multiplexer.multiplexer_constants import peers, types
from obci.drivers import drivers_logging as logger
from obci.configs import settings
#from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.control.launcher.launcher_tools import obci_root
import json

DISCOVERY_MODULE_NAMES = [
                        'amplifier_virtual_discovery',
                        'amplifier_tmsi_bt_discovery',
			'amplifier_gtec_usb_discovery',
                        'amplifier_tmsi_usb_discovery']
BASE_MODULE = 'obci.drivers.eeg.driver_discovery'

discovery_modules = []

LOGGER = logger.get_logger("DriverDiscovery", "info")

for mod_name in DISCOVERY_MODULE_NAMES:
    name = BASE_MODULE + '.' + mod_name
    try:
        __import__(name)
        discovery_modules.append(sys.modules[name])
    except:
        LOGGER.warning("Failed to load discovery module: " + mod_name)

def find_drivers():
    return _find_amps(discovery_modules)

def _filter_modules(pattern):
    return [sys.modules[BASE_MODULE + '.' + mod] for mod in \
                            DISCOVERY_MODULE_NAMES if pattern in mod]

def _find_amps(module_list):
    descriptions = []
    for mod in module_list:
        try:
            descriptions += mod.driver_descriptions()
        except Exception as e:
            LOGGER.warning("Discovery failed: " +  str(mod))
    return descriptions

def find_usb_amps():
    modules = _filter_modules('usb')
    return _find_amps(modules)

def find_bluetooth_amps():
    modules = _filter_modules('bt')
    return _find_amps(modules)

def find_virtual_amps():
    modules = _filter_modules('virtual')
    return _find_amps(modules)

if __name__ == '__main__':
    drivers = find_drivers()
    import json
    print json.dumps(drivers, indent=4)
