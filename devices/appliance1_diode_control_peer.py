#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#      Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

from devices import diode_control_peer
from devices import appliance1
class Appliance1DodeControl(diode_control_peer.DiodeControl):
    def _init_blinker(self):
        # an update request can be handled for config elements listed below:
        # save needed configuration.
        self.blinker = appliance1.Blinker(self.config.get_param("dev_path"))
        self.blinker.open()

if __name__ == "__main__":
    Appliance1DiodeControl(settings.MULTIPLEXER_ADDRESSES).loop()

