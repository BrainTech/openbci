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
>>> from openbci.data_storage import data_file_proxy as p

>>> import settings, os.path

>>> # PREPARE SOME SAMPLE FILE *************************************************

>>> px = p.DataFileWriteProxy('./tescik.obci.dat')

>>> px.data_received(1.2)

>>> px.data_received(0.0023)

>>> px.data_received(-123.456)

>>> px.data_received(3.3)

>>> px.data_received(5.0)

>>> px.data_received(0.0)

>>> nic = px.finish_saving()

>>> f = './tescik.obci.dat'

>>> from openbci.data_storage import read_data_source as s

>>> # TEST MEMORY DATA SOURCE **************************************************

>>> py = s.MemoryDataSource(2,3)

>>> py.add_sample(0, [1.0, 2.0])

>>> py.get_samples(0, 1)
array([[ 1.],
       [ 2.]])

>>> py.add_sample(3, [3.0, 4.0])
Traceback (most recent call last):
...
IndexError: invalid index

>>> py.add_sample(2, [1.0, 2.0, 3.0])
Traceback (most recent call last):
...
ValueError: shape mismatch: objects cannot be broadcast to a single shape

>>> # TEST FILE DATA SOURCE ****************************************************

>>> py = s.FileDataSource(f, 2, 3)

>>> py.get_samples(0, 0)
array([], shape=(2, 0), dtype=float64)

>>> py.get_samples(0, 2)
array([[  1.20000000e+00,  -1.23456000e+02],
       [  2.30000000e-03,   3.30000000e+00]])

>>> py.get_samples(0, 10)
Traceback (most recent call last):
...
NoNextValue

>>> py.get_samples(0, 3)
array([[  1.20000000e+00,  -1.23456000e+02,   5.00000000e+00],
       [  2.30000000e-03,   3.30000000e+00,   0.00000000e+00]])


>>> py.get_samples(1, 3)
Traceback (most recent call last):
...
NoNextValue

>>> py.get_samples()
array([[  1.20000000e+00,  -1.23456000e+02,   5.00000000e+00],
       [  2.30000000e-03,   3.30000000e+00,   0.00000000e+00]])


>>> py = s.FileDataSource(f, 2, 4)

>>> py.get_samples()
array([[  1.20000000e+00,  -1.23456000e+02,   5.00000000e+00,
          0.00000000e+00],
       [  2.30000000e-03,   3.30000000e+00,   0.00000000e+00,
          0.00000000e+00]])


>>> py = s.FileDataSource(f, 2, 2)

>>> py.get_samples()
array([[  1.20000000e+00,  -1.23456000e+02],
       [  2.30000000e-03,   3.30000000e+00]])

>>> py.get_samples()
array([[  1.20000000e+00,  -1.23456000e+02],
       [  2.30000000e-03,   3.30000000e+00]])



>>> os.remove(f)


"""

if __name__ == '__main__':
    import doctest, sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")

