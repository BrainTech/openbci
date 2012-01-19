#!/usr/bin/env python
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
"""
>>> e = test0()

>>> e.class_template
<class '__main__.A'>

>>> len(e.params) == 2*3
True

>>> e.params
[{'y': 'a', 'x': 1}, {'y': 'a', 'x': 2}, {'y': 'a', 'x': 3}, {'y': 'b', 'x': 1}, {'y': 'b', 'x': 2}, {'y': 'b', 'x': 3}]

>>> test1().params
[{}]

>>> cands, res = test2([10, 20])

>>> cands[0].X, cands[0].Y
(3, 'aa')

>>> cands[1].Z
10
>>> c = test3()

>>> cands, res = c.process([10])

>>> len(c.candidates) == 2*3*3*5
True

>>> cands[0].Z, cands[1].Z, cands[2].X, cands[2].Y
(20, 300, 3, 'dddd')

>>> res > 320
True

"""
from classification.chain import Chain, ChainElement
def test0():
    class A(object):
        pass
    elem = ChainElement(A, {'x':[1,2,3],
                            'y':['a','b']}
                        )
    return elem

def test1():
    class A(object):
        pass
    elem = ChainElement(A, {})
    return elem
    

def test2(data):
    class A(object):
        def __init__(self, x, y):
            self.X = x
            self.Y = y
        def process(self, data):
            return self.X + len(self.Y)


    class B(object):
        def __init__(self):
            self.Z = 10
            
        def process(self, data):
           return data

    c = Chain(
        ChainElement(A, {'x':[1,2,3],
                         'y':['aa','b']}),
        ChainElement(B, {})
        )

    return c.process(data)

def test3():
    class A(object):
        def __init__(self, x, y):
            self.X = x
            self.Y = y
        def process(self, data):
            return (self.X + len(self.Y)) / float(data[0]) + data[1]


    class B(object):
        def __init__(self, z):
            self.Z = z
            
        def process(self, data):
           return (self.Z, data[0] + self.Z)

    c = Chain(
        ChainElement(B, {'z':[10, 20]}),
        ChainElement(B, {'z':[100, 200, 300]}),
        ChainElement(A, {'x':[1,2,3],
                         'y':['aaa','b', 'cc', 'dddd', 'e']})
        )

    return c

if __name__=='__main__':
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
    print("ALL TESTS SUCCEEDED")
