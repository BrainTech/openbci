# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

"""
>>> from obci.analysis.obci_signal_processing.signal.data_read_proxy import DataReadProxy

>>> from obci.analysis.obci_signal_processing.signal.data_raw_write_proxy import DataRawWriteProxy

>>> import os.path, os

>>> px = DataRawWriteProxy('./tescik.obci.dat')

>>> px.set_data_len(1, 1)

>>> px.data_received(1.2)

>>> px.data_received(0.0023)

>>> px.data_received(-123.456)

>>> px.data_received(3.3)

>>> px.data_received(5.0)

>>> nic = px.finish_saving()

>>> f = './tescik.obci.dat'

>>> py = DataReadProxy(f)

>>> abs(1.2 - py.get_next_value()) < 0.0001
True

>>> abs(0.0023-py.get_next_value()) < 0.000000001
True

>>> abs(-123.456-py.get_next_value()) < 0.00001
True

>>> py.goto_value(1)

>>> abs(0.0023-py.get_next_value()) < 0.000000001
True

>>> py.goto_value(4)

>>> abs(5.0-py.get_next_value()) < 0.0001
True

>>> py.goto_value(6)

>>> py.get_next_value()
Traceback (most recent call last):
...
NoNextValue

>>> py.finish_reading()

>>> py.start_reading()

>>> vs = py.get_next_values(3)

>>> abs(vs[0]-1.20000000e+00)+abs(vs[1]-2.30000000e-03)+abs(vs[2]+1.23456000e+02)<3*0.0001
True

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
