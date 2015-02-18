# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

"""
>>> from obci.exps.ventures.calibration2_game.level_selector import LevelSelector, BinaryManager

>>> b = BinaryManager(0, 0)#[0]

>>> b.get_current()
(0, True)

>>> b = BinaryManager(5, 5)#[5]

>>> b.get_current()
(5, True)

>>> b = BinaryManager(0, 1)#[0,1]

>>> b.get_current()
(1, True)

>>> b = BinaryManager(0, 2)#[0,1,2]

>>> b.get_current()
(1, False)

>>> b = BinaryManager(5, 7)#[5,6,7]

>>> b.get_current()
(6, False)

>>> b = BinaryManager(5, 6)#[5,6]

>>> b.get_current()
(6, True)

>>> b = BinaryManager(5, 8)#[5,6,7,8]

>>> b.get_current()
(7, False)

>>> b = BinaryManager(5, 9)#[5,6,7,8,9]

>>> b.get_current()
(7, False)

>>> #######################################################

>>> s = LevelSelector([10*i for i in range(10)]) #[0..90], target = 40 

>>> s.get_level()
50

>>> s.update_level_result(True)
0

>>> s.get_level()
80

>>> s.update_level_result(False)
0

>>> s.get_level()
70

>>> s.update_level_result(False)
0

>>> s.get_level()
60

>>> s.update_level_result(False)
0

>>> s.get_level()
50


>>> s.update_level_result(False)
0

>>> s.get_level()
40

>>> s.update_level_result(True)
1

>>> #######################################################

>>> s = LevelSelector([10*i for i in range(10)]) #[0..90], target = 90

>>> s.get_level()
50

>>> s.update_level_result(True)
0

>>> s.get_level()
80

>>> s.update_level_result(True)
0

>>> s.get_level()
90

>>> s.update_level_result(True)
1

>>> #######################################################

>>> s = LevelSelector([10*i for i in range(10)]) #[0..90], target = -1

>>> s.get_level()
50

>>> s.update_level_result(False)
0

>>> s.get_level()
20

>>> s.update_level_result(False)
0

>>> s.get_level()
10

>>> s.update_level_result(False)
0

>>> s.get_level()
0

>>> s.update_level_result(False)
2

>>> #######################################################

>>> s = LevelSelector([10*i for i in range(10)]) #[0..90], target = -1

>>> s.get_level()
50

>>> s.update_level_result(False)
0

>>> s.get_level()
20

>>> s.update_level_result(True)
0

>>> s.get_level()
40

>>> s.update_level_result(False)
0

>>> s.get_level()
30

>>> s.update_level_result(False)
0

>>> s.get_level()
20

>>> s.update_level_result(False)
0

>>> s.get_level()
10

>>> s.update_level_result(False)
0

>>> s.get_level()
0

>>> s.update_level_result(False)
2

>>> #######################################################

>>> s = LevelSelector([10*i for i in range(9)]) #[0..80], target = 70

>>> s.get_level()
40

>>> s.update_level_result(True)
0

>>> s.get_level()
70

>>> s.update_level_result(True)
0

>>> s.get_level()
80

>>> s.update_level_result(False)
0

>>> s.get_level()
70

>>> s.update_level_result(True)
1


"""

def run():
    import doctest, sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")

if __name__ == '__main__':
    run()
