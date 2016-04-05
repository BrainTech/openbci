# -*- coding: utf-8 -*-
#!/usr/bin/env python
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

"""
>>> import os

>>> from obci.analysis.obci_signal_processing.signal import info_file_proxy as p

>>> px = p.InfoFileWriteProxy('./tescik.obci.svarog.info')

>>> px.set_attributes({'number_of_channels':2, 'sampling_frequency':128, 'channels_names': ['1','2'], 'file':'soufce.obci.dat', 'number_of_samples':3})

>>> px.finish_saving()
'./tescik.obci.svarog.info'

>>> py = p.InfoFileReadProxy('./tescik.obci.svarog.info')

>>> print(py.get_param('number_of_channels'))
2

>>> print(py.get_param('channels_names')[0])
1

>>> os.remove('./tescik.obci.svarog.info')

"""
def run():
    import doctest, sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")

if __name__ == '__main__':
    run()
