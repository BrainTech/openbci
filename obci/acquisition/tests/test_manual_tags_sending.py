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
import random
def run():
    while True:
        i = raw_input()
        print("LEN i: "+str(len(i)))
        if len(i) == 0:
            i = "XYZ"
        i =  i.strip()
        t= time.time()
        print("SEND TAG name"+i+" with time: "+repr(t))
        TAGGER.send_tag(t, t+3.0*random.random()+1.0, i, {'a':1, 'b':2.2, 'c':'napis_jakis', 'annotation':"ANNOTACJA JAKAS"})

if __name__ == "__main__":
    print("Type anything to send tag!!!")
    run()
