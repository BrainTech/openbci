#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
#from multiplexer.multiplexer_constants import peers, types
from drivers import drivers_logging as logger
from obci_configs import settings
#from peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from launcher.launcher_tools import obci_root
import json

DISCOVERY_MODULE_NAMES = [
                        'amplifier_virtual_discovery',
                        'amplifier_tmsi_bt_discovery',
                        'amplifier_tmsi_usb_discovery']
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

# class DriverDiscovery(ConfiguredMultiplexerServer):
#     def __init__(self, addresses):
#         super(DriverDiscovery, self).__init__(addresses=addresses, type=peers.DRIVER_DISCOVERY)

#         self._mx_addresses = addresses

#         self.drivers = find_drivers()
#         self.serialize_drivers_info(self.drivers)

#         self.ready()

#         # 00:A0:96:1B:48:4B       Mobi5 0925100001
#         # 00:A0:96:1B:42:DC       MobiMini 0931080004
#         # 00:A0:96:1B:48:DB       Porti7-24e4b4at 0207090008


#     def _add_driver(self, driver_desc):
#         desc = json.loads(driver_desc)
#         self.drivers.append(desc)

#     def serialize_drivers_info(self, driver_list):
#         self.set_param('available_drivers', driver_list)


if __name__ == '__main__':
    # DriverDiscovery(settings.MULTIPLEXER_ADDRESSES).loop()
    drivers = find_drivers()
    import json
    print json.dumps(drivers, indent=4)