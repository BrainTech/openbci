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
>>> from ..signal import data_file_proxy as p

>>> import settings, os.path

>>> px = p.DataFileWriteProxy('./tescik.obci.dat')

>>> px.data_received(1.2)

>>> px.data_received(0.0023)

>>> px.data_received(-123.456)

>>> px.data_received(3.3)

>>> px.data_received(5.0)

>>> nic = px.finish_saving()

>>> f = './tescik.obci.dat'

>>> py = p.DataFileReadProxy(f)

>>> py.get_next_value()
1.2

>>> py.get_next_value()
0.0023

>>> py.get_next_value()
-123.456

>>> py.goto_value(1)

>>> py.get_next_value()
0.0023

>>> py.goto_value(4)

>>> py.get_next_value()
5.0

>>> py.goto_value(6)

>>> py.get_next_value()
Traceback (most recent call last):
...
NoNextValue

>>> py.finish_reading()

>>> py.start_reading()

>>> py.get_next_values(3)
array([  1.20000000e+00,   2.30000000e-03,  -1.23456000e+02])

>>> py.get_next_values(3)
Traceback (most recent call last):
...
NoNextValue
>>> #warning here

>>> os.remove(f)


"""
def run():
    import doctest, sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")

if __name__ == '__main__':
    run()
