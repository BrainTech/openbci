#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#      Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

import time
from devices import diode_control_peer
from devices import appliance1
from devices import appliance2
from devices import appliance_dummy
from obci_configs import settings

class ApplianceDiodeControl(diode_control_peer.DiodeControl):
    def __init__(self, addresses):
        super(ApplianceDiodeControl, self).__init__(addresses=addresses)

    def _init_blinker(self):
        app = self.config.get_param('current_appliance')
        if app == 'appliance1':
            self.blinker = appliance1.Blinker(self.config.get_param("device_path"))
            self.blinker.open()

        elif app == 'appliance2':
            self.blinker = appliance2.Blinker(self.config.get_param("device_path"))
            self.blinker.open()
            self.blinker.set_intensity(int(self.config.get_param("intensity")))
            time.sleep(1) #TODO - without it if just-after _init_blinker freqs will be sent - it will not work (possibly there m            
        elif app == 'dummy':
            self.blinker = appliance_dummy.Blinker()
            self.blinker.open()

        else:
            self.logger.error("Unrecognised appliance name: "+str(app))

if __name__ == "__main__":
    ApplianceDiodeControl(settings.MULTIPLEXER_ADDRESSES).loop()

