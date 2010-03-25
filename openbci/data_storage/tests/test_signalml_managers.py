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
>>> from openbci.data_storage import signalml_save_manager, signalml_read_manager

>>> import os

>>> svr = signalml_save_manager.SignalmlSaveManager('tescik', './', {'number_of_channels':2, 'sampling_frequency':128, 'channels_names': ['1','2']})

>>> svr.data_received(float(1), 1.0)

>>> svr.data_received(float(2), 2.0)

>>> (inf, dat, tags, timestamps) = svr.finish_saving()


>>> mgr = signalml_read_manager.SignalmlReadManager(inf, dat)

>>> mgr.start_reading()

>>> mgr.get_next_value()
1.0

>>> mgr.get_next_value()
2.0

>>> mgr.get_next_value()
Traceback (most recent call last):
...    
NoNextValue


>>> mgr.get_param(u'file')
u'tescik.obci.dat'

>>> mgr.get_param(u'number_of_samples')
u'2'

>>> mgr.get_param(u'sampling_frequency')
u'128'

>>> mgr.get_param('channels_names')
[u'1', u'2']

>>> mgr.get_param('im_not_there')
Traceback (most recent call last):
...
NoParameter: No parameter 'im_not_there' was found in info xml file!

>>> os.system("rm tescik.obci.info")
0

>>> os.system("rm tescik.obci.dat")
0

"""
if __name__ == '__main__':
    import doctest, sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")
