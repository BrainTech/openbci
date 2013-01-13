#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>
from obci.devices import appliance1
from obci.devices import appliance2
from obci.devices import appliance_dummy

def get_blinker(app, dev_path=None, intensity=None):
    blinker = None
    if app == 'appliance1':
        blinker = appliance1.Blinker(dev_path)
        blinker.open()
    elif app == 'appliance2':
        blinker = appliance2.Blinker(dev_path)
        blinker.open()
        if intensity is not None:
            blinker.set_intensity(intensity)
    elif app == 'dummy':
        blinker = appliance_dummy.Blinker()
        blinker.open()
    return blinker
