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
"""
>>> from ..tags import smart_tag_definition as d
>>> x = d.SmartTagDurationDefinition(start_tag_name='x', start_offset=1, end_offset=0, duration=21)

>>> print(x.__dict__['start_tag_name'])
x

>>> print(x.__dict__['start_offset'])
1

>>> print(x.__dict__['end_offset'])
0

>>> print(x.__dict__['duration'])
21

"""
def run():
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
    print("All tests succeeded!")
        
        
if __name__=='__main__':
    run()
