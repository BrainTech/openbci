#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#      Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

import time, sys, signal
from obci.configs import settings
from obci.devices import blinker_factory
from obci.devices import appliance_diode_control_peer
from obci.control.peer.configured_client import ConfiguredClient
from multiplexer.multiplexer_constants import peers, types
from obci.utils.openbci_logging import log_crash

class ApplianceCleaner(ConfiguredClient):
    @log_crash
    def __init__(self, addresses):
        super(ApplianceCleaner, self).__init__(settings.MULTIPLEXER_ADDRESSES, type=peers.CLIENT)
        self.ready()
        self.init_blinker()
        self.init_signals()

    def init_blinker(self):
        app = self.config.get_param('current_appliance')
        if app == 'appliance1' or app == 'appliance2':
            self.blinker = blinker_factory.get_blinker(
                app,
                self.config.get_param("device_path"))
        elif app == 'dummy':
            self.blinker = blinker_factory.get_blinker(app)
        else:
            self.logger.error("Unrecognised appliance name: "+str(app))

    def init_signals(self):
        self.logger.info("INIT SIGNALS IN APPLIANCE CLEANER")
        signal.signal(signal.SIGTERM, self.signal_handler())
        signal.signal(signal.SIGINT, self.signal_handler())
        
    def signal_handler(self):
        def handler(signum, frame):
            self.logger.info("Got signal " + str(signum) + "!!! Sending diodes ON!")
            self.blinker.on()
            sys.exit(-signum)
        return handler

if __name__ == "__main__":
    ApplianceCleaner(settings.MULTIPLEXER_ADDRESSES)
    while True:
        time.sleep(10)

