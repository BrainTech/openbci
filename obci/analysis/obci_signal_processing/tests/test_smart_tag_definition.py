#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""
>>> from obci.analysis.obci_signal_processing.tags import smart_tag_definition as d
>>> x = d.SmartTagDurationDefinition(start_tag_name='x', start_offset=1, end_offset=0, duration=21)

>>> print(x.__dict__['start_tag_name'])
x

>>> print(x.__dict__['start_offset'])
1

>>> print(x.__dict__['end_offset'])
0

>>> print(x.__dict__['duration'])
21

"""
def run():
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
    print("All tests succeeded!")
        
        
if __name__=='__main__':
    run()
