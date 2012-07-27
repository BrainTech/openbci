#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from drivers import drivers_logging as logger
from obci_configs import settings
from launcher.launcher_tools import obci_root
import json

DISCOVERY_MODULE_NAMES = [
                        'amplifier_virtual_discovery',
                        'amplifier_tmsi_bt_discovery',
                        'amplifier_tmsi_usb_discovery',
                        'amplifier_gtec_usb_discovery']
BASE_MODULE = 'drivers.eeg.driver_discovery'

discovery_modules = []


for mod_name in DISCOVERY_MODULE_NAMES:
    name = BASE_MODULE + '.' + mod_name
    __import__(name)
    discovery_modules.append(sys.modules[name])

LOGGER = logger.get_logger("DriverDiscovery", "info")

def find_drivers():
    return _find_amps(discovery_modules)

def _filter_modules(pattern):
    return [sys.modules[BASE_MODULE + '.' + mod] for mod in \
                            DISCOVERY_MODULE_NAMES if pattern in mod]

def _find_amps(module_list):
    descriptions = []
    for mod in module_list:
        descriptions += mod.driver_descriptions()
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
    with open("dump.txt", 'w') as f:
        f.write(json.dumps(drivers, indent=4))