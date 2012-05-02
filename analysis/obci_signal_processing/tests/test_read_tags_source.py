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
>>> tags = []

>>> tags.append({'start_timestamp':1001.0, 'end_timestamp':1002.0, 'name': 'nic', 'channels':'A B C', 'desc': {'x':123, 'y':456, 'z': 789}})

>>> tags.append({'start_timestamp':1003.0, 'end_timestamp':1004.0, 'name': 'nic2', 'channels':'A B C', 'desc': {'x':1234, 'y':4567, 'z': 789}})

>>> tags.append({'start_timestamp':1005.0, 'end_timestamp':1006.0, 'name': 'nic3', 'channels':'A B C', 'desc': {'x':12345, 'y':45678, 'z': 789}})

>>> tags.append({'start_timestamp':1005.5, 'end_timestamp':1007.0, 'name': 'nic2', 'channels':'A B C', 'desc': {'x':12345, 'y':45678, 'z': 789}})

>>> tags.append({'start_timestamp':1008.0, 'end_timestamp':1009.0, 'name': 'nic3', 'channels':'A B C', 'desc': {'x':12345, 'y':45678, 'z': 789}})

>>> from ..tags import read_tags_source

>>> s = read_tags_source.MemoryTagsSource(tags)

>>> s.get_tags()
[{'channels': 'A B C', 'start_timestamp': 1001.0, 'desc': {'y': 456, 'x': 123, 'z': 789}, 'name': 'nic', 'end_timestamp': 1002.0}, {'channels': 'A B C', 'start_timestamp': 1003.0, 'desc': {'y': 4567, 'x': 1234, 'z': 789}, 'name': 'nic2', 'end_timestamp': 1004.0}, {'channels': 'A B C', 'start_timestamp': 1005.0, 'desc': {'y': 45678, 'x': 12345, 'z': 789}, 'name': 'nic3', 'end_timestamp': 1006.0}, {'channels': 'A B C', 'start_timestamp': 1005.5, 'desc': {'y': 45678, 'x': 12345, 'z': 789}, 'name': 'nic2', 'end_timestamp': 1007.0}, {'channels': 'A B C', 'start_timestamp': 1008.0, 'desc': {'y': 45678, 'x': 12345, 'z': 789}, 'name': 'nic3', 'end_timestamp': 1009.0}]

>>> s.get_tags('nic2')
[{'channels': 'A B C', 'start_timestamp': 1003.0, 'desc': {'y': 4567, 'x': 1234, 'z': 789}, 'name': 'nic2', 'end_timestamp': 1004.0}, {'channels': 'A B C', 'start_timestamp': 1005.5, 'desc': {'y': 45678, 'x': 12345, 'z': 789}, 'name': 'nic2', 'end_timestamp': 1007.0}]

>>> s.get_tags(None, 1005.0, 1.0)
[{'channels': 'A B C', 'start_timestamp': 1005.0, 'desc': {'y': 45678, 'x': 12345, 'z': 789}, 'name': 'nic3', 'end_timestamp': 1006.0}, {'channels': 'A B C', 'start_timestamp': 1005.5, 'desc': {'y': 45678, 'x': 12345, 'z': 789}, 'name': 'nic2', 'end_timestamp': 1007.0}]

>>> s.get_tags('nic3', 1005.0, 1.0)
[{'channels': 'A B C', 'start_timestamp': 1005.0, 'desc': {'y': 45678, 'x': 12345, 'z': 789}, 'name': 'nic3', 'end_timestamp': 1006.0}]

>>> s.get_tags(None, None, None, lambda tag: tag['desc']['x'] == 12345)
[{'channels': 'A B C', 'start_timestamp': 1005.0, 'desc': {'y': 45678, 'x': 12345, 'z': 789}, 'name': 'nic3', 'end_timestamp': 1006.0}, {'channels': 'A B C', 'start_timestamp': 1005.5, 'desc': {'y': 45678, 'x': 12345, 'z': 789}, 'name': 'nic2', 'end_timestamp': 1007.0}, {'channels': 'A B C', 'start_timestamp': 1008.0, 'desc': {'y': 45678, 'x': 12345, 'z': 789}, 'name': 'nic3', 'end_timestamp': 1009.0}]


"""
def run():
    import doctest, sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")

if __name__ == '__main__':
    run()
