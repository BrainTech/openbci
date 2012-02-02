#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#      Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

from devices import diode_control_peer
from devices import appliance2
from configs import settings

class Appliance2DiodeControl(diode_control_peer.DiodeControl):
    def _init_blinker(self):
        # an update request can be handled for config elements listed below:
        # save needed configuration.
        self.blinker = appliance2.Blinker(self.config.get_param("device_path"))
        self.blinker.open()
        self.blinker.set_intensity(int(self.config.get_param("intensity")))

if __name__ == "__main__":
    Appliance2DiodeControl(settings.MULTIPLEXER_ADDRESSES).loop()

