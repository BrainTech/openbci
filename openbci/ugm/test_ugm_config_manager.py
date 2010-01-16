#!/Usr/bin/env python
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
#
"""
>>> import ugm_config_manager as m

>>> mgr = m.UgmConfigManager('ugm_config_for_tests_dont_touch_this_file')

>>> c = mgr.get_config_for(1)

>>> print(c['id'])
1

>>> print(c['color'])
#d4d4d4

>>> print(len(c['stimuluses']))
2

>>> print(c['stimuluses'][0]['id'])
11

>>> print(c['id'])
1

>>> c['id'] = 2

>>> print(c['id'])
2

>>> c = mgr.get_config_for(1)

>>> print(c['id'])
1


>>> also_c = mgr.get_ugm_fields()[0]

>>> print(also_c['id'])
1


>>> c = mgr.get_config_for(1)

>>> also_c = mgr.get_ugm_fields()[0]

>>> c == also_c
True

>>> mgr.set_config({'id':1, 'cos_tam':2})

>>> c = mgr.get_config_for(1)

>>> also_c = mgr.get_ugm_fields()[0]

>>> c == also_c
True

>>> print(also_c)
{'cos_tam': 2, 'id': 1}

>>> full = mgr.get_ugm_fields()

>>> mgr.update_to_file('trash.py')

>>> also_full = __import__('trash').fields

>>> full == also_full
True


""" 
if __name__ == '__main__':
    import doctest, sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")
