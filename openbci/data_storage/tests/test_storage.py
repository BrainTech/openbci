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



# First you should generate data_to_compare files...
# To do that:
# - go to data_storage/tests/data/ directory
# - delete data_to_compare* files
# - set 'file'/'dir' path in hashtable, so that it points to data_to_compare* files
# - fire test_data_storage
# - when storage is finished run: ./openbci/data_storage/tests/test_manually_signal_saver_control.py finish_saving
# - the run test_storage.py

"""
>>> from openbci.data_storage import read_manager

>>> import os, os.path

>>> from openbci import settings 

>>> f1 = os.path.join(settings.module_abs_path(),'data', 'data')

>>> f2 = os.path.join(settings.module_abs_path(),'data', 'data_to_compare')

>>> mgr1 = read_manager.ReadManager(f1+'.obci.info', f1+'.obci.dat', f1+'.obci.tags')

>>> mgr2 = read_manager.ReadManager(f2+'.obci.info', f2+'.obci.dat', f2+'.obci.tags')

>>> # Compare params files
>>> p1 = get_params(mgr1)

>>> p2 = get_params(mgr1)

>>> p1 == p2
True

>>> # Compare tags - start timestamps - int, as float comparison is often misleading
>>> t1 = [int(i) for i in get_tags_attr(mgr1, 'start_timestamp')]

>>> t2 = [int(i) for i in get_tags_attr(mgr2, 'start_timestamp')]

>>> t1 == t2
True

>>> t1 = get_tags_attr(mgr1, 'name')

>>> t1
[u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger', u'trigger']

>>> t2 = get_tags_attr(mgr2, 'name')

>>> t1 != t2
False


>>> #Compare data

>>> d1 = mgr1.get_samples()

>>> d2 = mgr2.get_samples()

>>> d1 == d2
array([[ True,  True,  True, ...,  True,  True,  True],
       [ True,  True,  True, ...,  True,  True,  True],
       [ True,  True,  True, ...,  True,  True,  True],
       ..., 
       [ True,  True,  True, ...,  True,  True,  True],
       [ True,  True,  True, ...,  True,  True,  True],
       [ True,  True,  True, ...,  True,  True,  True]], dtype=bool)


"""

def get_params(mgr):
    params = ['channels_names','channels_gains','channels_offsets',
              'number_of_samples','number_of_channels','sampling_frequency']
    ret = {}
    for p in params:
        ret[p] = mgr.get_param(p)

    return ret

def get_tags_attr(mgr, attr):
    attrs = []
    for tag in mgr.iter_tags():
        attrs.append(tag[attr])
    return attrs

if __name__ == '__main__':
    import doctest, sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")
