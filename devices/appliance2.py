#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#      Magdalena Michalska <jezzy.nietoperz@gmail.com>
#      Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>

from devices import appliance1

class Blinker(appliance1.Blinker):
    def set_intensity(self, v):
        str = chr(5)
        str+=chr(v)
        self.send(str)
        
