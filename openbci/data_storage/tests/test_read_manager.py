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
>>> from openbci.data_storage import read_manager

>>> import os, os.path

>>> from openbci import settings 

>>> f = os.path.join(settings.module_abs_path(),'data', 'data')

>>> mgr = read_manager.ReadManager(f+'.obci.svarog.info', f+'.obci.dat', None)

>>> mgr.get_samples(0, 1)[0,0]
-27075.0


>>> mgr.get_samples(0, 1)[1,0]
39641.0


>>> ch = mgr.get_samples()


>>> ch[0][0]
-27075.0

>>> ch[1][0]
39641.0

>>> [len(x) for x in ch]
[112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407, 112407]


>>> mgr.get_param(u'number_of_samples')
u'2810175'

>>> mgr.get_param(u'sampling_frequency')
u'128'

>>> mgr.get_param(u'number_of_channels')
u'25'

>>> mgr.get_param('channels_names')
[u'Fp1', u'Fpz', u'Fp2', u'F7', u'F3', u'Fz', u'F4', u'F8', u'M1', u'C7', u'C3', u'Cz', u'C4', u'T8', u'M2', u'P7', u'P3', u'Pz', u'P4', u'P8', u'O1', u'Oz', u'O2', u'NIC', u'OKO_GORA_DOL']


>>> mgr.get_param('im_not_there')
Traceback (most recent call last):
...
NoParameter: No parameter 'im_not_there' was found in info xml file!





"""
if __name__ == '__main__':
    import doctest, sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")
