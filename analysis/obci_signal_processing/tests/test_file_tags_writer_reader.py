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
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

"""
>>> from ..tags import tags_file_writer as p

>>> from ..tags import tags_file_reader as t

>>> px = p.TagsFileWriter('./tescik.obci.tags')

>>> px.tag_received({'start_timestamp':1001.0, 'end_timestamp':1002.0, 'name': 'nic', 'channels':'A B C', 'desc': {'x':123, 'y':456, 'z': 789}})

>>> px.tag_received({'start_timestamp':1003.0, 'end_timestamp':1004.0, 'name': 'nic2', 'channels':'A B C', 'desc': {'x':1234, 'y':4567, 'z': 789}})

>>> px.tag_received({'start_timestamp':1005.0, 'end_timestamp':1006.0, 'name': 'nic3', 'channels':'A B C', 'desc': {'x':12345, 'y':45678, 'z': 789}})

>>> px.finish_saving(1000.0)
'./tescik.obci.tags'

>>> py = t.TagsFileReader('tescik.obci.tags')

>>> g = py.get_tags()[0]

>>> print(g['start_timestamp'])
1.0

>>> print(g['end_timestamp'])
2.0

>>> print(g['name'])
nic

>>> print(g['desc']['y'])
456

>>> print([int(t['start_timestamp']) for t in py.get_tags()])
[1, 3, 5]


>>> #REORDER AND TEST ORDERING AGAIN ....

>>> px = p.TagsFileWriter('./tescik.obci.tags')

>>> px.tag_received({'start_timestamp':1003.0, 'end_timestamp':1004.0, 'name': 'nic2', 'channels':'A B C', 'desc': {'x':1234, 'y':4567, 'z': 789}})

>>> px.tag_received({'start_timestamp':1005.0, 'end_timestamp':1006.0, 'name': 'nic3', 'channels':'A B C', 'desc': {'x':12345, 'y':45678, 'z': 789}})

>>> px.tag_received({'start_timestamp':1001.0, 'end_timestamp':1002.0, 'name': 'nic', 'channels':'A B C', 'desc': {'x':123, 'y':456, 'z': 789}})

>>> print([int(t['start_timestamp']) for t in py.get_tags()])
[1, 3, 5]

>>> import os

>>> os.system('rm tescik*')
0

>>> 
"""
def run():
    import doctest, sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")

if __name__ == '__main__':
    run()
