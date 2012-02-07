#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#      Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

from devices import diode_control_peer
from devices import appliance1
from configs import settings

class Appliance1DiodeControl(diode_control_peer.DiodeControl):
    def __init__(self, addresses):
        super(Appliance1DiodeControl, self).__init__(addresses=addresses)

    def _init_blinker(self):
        self.blinker = appliance1.Blinker(self.config.get_param("device_path"))
        self.blinker.open()

if __name__ == "__main__":
    Appliance1DiodeControl(settings.MULTIPLEXER_ADDRESSES).loop()

