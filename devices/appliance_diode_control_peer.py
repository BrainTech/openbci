#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#      Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

from obci.devices import diode_control_peer
from obci.configs import settings
from obci.devices import blinker_factory
import time

class ApplianceDiodeControl(diode_control_peer.DiodeControl):
    def __init__(self, addresses):
        super(ApplianceDiodeControl, self).__init__(addresses=addresses)

    def _init_blinker(self):
        #local config overwrites global, if exists
        app = self.config.get_param('current_appliance')
        if len(app) == 0:
            app = settings.current_appliance()
            self.config.set_param('current_appliance', app)

        if app == 'appliance1':
            self.blinker = blinker_factory.get_blinker(
                app,
                self.config.get_param("device_path"))
        elif app == 'appliance2':
           self.blinker = blinker_factory.get_blinker(
                app,
                self.config.get_param("device_path"),
                int(self.config.get_param("intensity")))
           time.sleep(1) #TODO - without it if just-after _init_blinker freqs will be sent - it will not work (possibly there m            
        elif app == 'dummy':
            self.blinker = blinker_factory.get_blinker(app)
        else:
            self.logger.error("Unrecognised appliance name: "+str(app))

if __name__ == "__main__":
    ApplianceDiodeControl(settings.MULTIPLEXER_ADDRESSES).loop()

