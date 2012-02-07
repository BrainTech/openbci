#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from multiplexer.multiplexer_constants import peers, types
from drivers import drivers_logging as logger
from configs import settings
from peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from launcher.launcher_tools import obci_root
import json

DISCOVERY_MODULE_NAMES = ['amplifier_virtual_discovery', 'amplifier_tmsi_discovery']
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
            descriptions += mod.driver_descriptions()
        return descriptions

        # 00:A0:96:1B:48:4B       Mobi5 0925100001
        # 00:A0:96:1B:42:DC       MobiMini 0931080004
        # 00:A0:96:1B:48:DB       Porti7-24e4b4at 0207090008


    def _add_driver(self, driver_desc):
        desc = json.loads(driver_desc)
        self.drivers.append(desc)

    def serialize_drivers_info(self, driver_list):
        self.set_param('available_drivers', driver_list)


if __name__ == '__main__':
    DriverDiscovery(settings.MULTIPLEXER_ADDRESSES).loop()