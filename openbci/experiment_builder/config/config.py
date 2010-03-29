# -*- coding: utf-8 -*-
#!/usr/bin/env python
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
#      Łukasz Polak <l.polak@gmail.com>
#
"""Holds experiment builder config"""

DUPA = 3
CONFIG = {}
CONFIG['screens'] = [
#        ['zosia/strz1', 'zosia/strz2'], 
        ['ania/mk-mo', 'ania/sk-mo', 'ania/dk-mo'],
        ['zosia/wiel1', 'zosia/wiel2', 'zosia/wiel3', 'zosia/wiel4']
#        ['zosia/kolc', 'zosia/koln', 'zosia/kolrozne', 'zosia/kolziel', 'zosia/kolzol'],
#        ['zosia/pf0', 'zosia/pf1'],
#        ['zosia/wielodl1', 'zosia/wielodl3'],
#        ['ania/sk-mo', 'ania/mk-mo', 'ania/dk-mo'], 
]

# [square1, 2, 3, 4,
#        5, 6, 7, 8]
CONFIG['freqs'] = [
    [
        [70, 12, 15, 70, 70, 13, 14, 70], # 'ania/mk-mo'
        [70, 12, 15, 70, 70, 13, 14, 70], # 'ania/sk-mo'
        [70, 12, 15, 70, 70, 13, 14, 70]], # etc....
    [
        [70, 12, 15, 70, 70, 13, 14, 70],  # 'zosia/wiel1'
        [70, 12, 15, 70, 70, 13, 14, 70],  # 'zosia/wiel2'
        [70, 12, 15, 70, 70, 13, 14, 70], # ...
        [70, 12, 15, 70, 70, 13, 14, 70]]
        ]
CONFIG['delay'] = 10
CONFIG['repeats'] = 40
CONFIG['readable_names'] = {
    'ania/mk-mo' : 'murr',
    'ania/sk-mo' : 'surr',
    'ani/dk-mo' : 'durr',
    'zosia/wiel1' : 'w1rr',
    'zosia/wiel2' : 'w2rr',
    'zosia/wiel3' : 'w3rr',
    'zosia/wiel4' : 'w4rr',
}

USE_MULTIPLEXER = True      

# set this to True and set DEFAULT_FREQS to use one frequencies set for all
# screens. Then you can omit defining CONFIG['freqs']
USE_DEFAULT_FREQS = False

DEFAULT_FREQS = [60, 12, 15, 60, 60, 13, 14, 60]
