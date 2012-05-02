# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

"""
>>> from ..signal import data_file_proxy as p
variables_pb2 import failed!!! Mx part of the class will not work

>>> import os.path, os

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
