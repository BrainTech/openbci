#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#      Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

import time, sys, signal
from obci_configs import settings

from devices import appliance1
from devices import appliance2
from devices import appliance_dummy
from devices import appliance_diode_control_peer
from obci_control.peer.configured_client import ConfiguredClient
from multiplexer.multiplexer_constants import peers, types

from devices import devices_logging as logger
LOGGER = logger.get_logger('appliance_cleaner')


class ApplianceCleaner(ConfiguredClient):
    def __init__(self, addresses):
        super(ApplianceCleaner, self).__init__(settings.MULTIPLEXER_ADDRESSES, type=peers.CLIENT)
        self.ready()
        self.init_blinker()
        self.init_signals()

    def init_blinker(self):
        app = self.config.get_param('current_appliance')
        if app == 'appliance1':
            self.blinker = appliance1.Blinker(self.config.get_param("device_path"))
        elif app == 'appliance2':
            self.blinker = appliance2.Blinker(self.config.get_param("device_path"))
        elif app == 'dummy':
            self.blinker = appliance_dummy.Blinker()
        else:
            LOGGER.error("Unrecognised appliance name: "+str(app))
            sys.exit(1)
        self.blinker.open()

    def init_signals(self):
        LOGGER.info("INIT SIGNALS IN APPLIANCE CLEANER")
        signal.signal(signal.SIGTERM, self.signal_handler())
        signal.signal(signal.SIGINT, self.signal_handler())
        
    def signal_handler(self):
        def handler(signum, frame):
            LOGGER.info("Got signal " + str(signum) + "!!! Sending diodes ON!")
            self.blinker.on()
            sys.exit(-signum)
        return handler

if __name__ == "__main__":
    ApplianceCleaner(settings.MULTIPLEXER_ADDRESSES)
    while True:
        time.sleep(10)

