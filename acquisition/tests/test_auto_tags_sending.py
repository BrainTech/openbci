#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

from tags import tagger
import time

TAGGER = tagger.get_tagger()
COLORS = ['czerwony', 'zielony', 'niebieski', 'bialy']
NAMES = ['pozytywny', 'negatywny', 'neutralny']
import random
def run():
    while True:
        time.sleep(1.0 + random.random()*10.0)
        name = NAMES[random.randint(0, len(NAMES)-1)]

        t= time.time()
        print("SEND TAG name"+name+" with time: "+repr(t))
        if name == 'pozytywny' or name == 'negatywny':
            TAGGER.send_tag(t, 1.0, name, {'czestosc':random.randint(0, 10),
                                                              'liczba':random.random(), 
                                                              'wypelnienie':COLORS[random.randint(0, len(COLORS)-1)], 
                                                              'tekst': " d jfsld fkjew lkgjew lkgjewlkg jewg ldsj glkds jglkdsg jlkdsg jds"
                                                                 })
        else:
            TAGGER.send_tag(t, 1.0, name, {'czestosc':random.randint(0, 10),
                                           'wypelnienie':COLORS[random.randint(0, len(COLORS)-1)], 
                                           'poziom': random.randint(100, 1000)})

if __name__ == "__main__":
    print("Type anything to send tag!!!")
    run()
