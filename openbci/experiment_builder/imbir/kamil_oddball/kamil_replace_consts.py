#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kamil_consts import *


old_f_name = 'kamil_oddball_10_01_2010.py'
dir = './'

new_f_name = old_f_name +'.fixed.py'


old_f = open(dir+old_f_name, 'r')
new_f = open(dir+new_f_name, 'w')

for old_line in old_f:
    line = str(old_line)
    for i in range(NUM_OF_VALS):
        to_replace = str(float(START_ST + i))
        line = line.replace(to_replace, 's_st['+str(i)+']')
        to_replace = str(float(START_DUR + i))
        line = line.replace(to_replace, 's_dur['+str(i)+']')
        to_replace = str(float(START_DUR + START_ST + 2+(NUM_OF_VALS-1)))+'000'
        line = line.replace(to_replace, 's_dur[-1]+s_st[-1]')

        
    new_f.write(line)
new_f.close()
old_f.close()
