#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from multiplexer.multiplexer_constants import peers, types
from drivers import drivers_logging as logger
from configs import settings
from peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from launcher.launcher_tools import obci_root
import json

DISCOVERY_MODULE_NAMES = ['amplifier_virtual_discovery']
discovery_modules = []

for mod_name in DISCOVERY_MODULE_NAMES:
    mod = __import__(mod_name)
    discovery_modules.append(mod)

LOGGER = logger.get_logger("DriverDiscovery", "info")

class DriverDiscovery(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(DriverDiscovery, self).__init__(addresses=addresses, type=peers.DRIVER_DISCOVERY)

        self._mx_addresses = addresses

        self.drivers = self.find_drivers()
        self.serialize_drivers_info(self.drivers)

        self.ready()


    def find_drivers(self):
        descriptions = []
        for mod in discovery_modules: 
            if mod.driver_available():
                descriptions.append(mod.driver_description())
        return descriptions
        

    def _add_driver(self, driver_desc):
        desc = json.loads(driver_desc)
        self.drivers.append(desc)

    def serialize_drivers_info(self, driver_list):
        self.set_param('available_drivers', driver_list)


if __name__ == '__main__':
    DriverDiscovery(settings.MULTIPLEXER_ADDRESSES).loop()