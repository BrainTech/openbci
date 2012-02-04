#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#      Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

import time
from devices import diode_control_peer
from devices import appliance2
from configs import settings

class Appliance2DiodeControl(diode_control_peer.DiodeControl):
    def __init__(self, addresses):
        super(Appliance2DiodeControl, self).__init__(addresses=addresses)

    def _init_blinker(self):
        self.blinker = appliance2.Blinker(self.config.get_param("device_path"))
        self.blinker.open()
        #self.blinker.set_intensity(int(self.config.get_param("intensity")))
        #time.sleep(3) #TODO - without it if just-after _init_blinker freqs will be sent - it will not work (possibly there must be some break between two commands to the device)

if __name__ == "__main__":
    Appliance2DiodeControl(settings.MULTIPLEXER_ADDRESSES).loop()

