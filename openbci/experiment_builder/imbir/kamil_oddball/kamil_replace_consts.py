#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kamil_consts import *


old_f_name = 'kamil_oddball_10_01_2010.py'
dir = './'

new_f_name = old_f_name +'.fixed.py'


old_f = open(dir+old_f_name, 'r')
new_f = open(dir+new_f_name, 'w')

for old_line in old_f:
    line = old_line

    #center strings - ugly hack
    string_indicator = 'text=u'
    if line.find(string_indicator) >= 0:
        print("REPLACING text...")
        start_ind = line.find(string_indicator)+len(string_indicator)+1
        end_ind = line.rfind("'")
        old_string = line[start_ind:end_ind]
        #first split string by lines
        old_lines = old_string.split('\\n')

        #center every line according to maximum line
        #do it manually as w have asci strings containing utf chars so len(line) gives false results
        max_line = -1
        for i in old_lines:
            ln = len(i)
            ln -= 5*i.count('\u')
            ln -= 3*i.count('\\x')
            if ln > max_line:
                max_line = ln
        
        #center manually
        old_lines_cent = []
        for i in range(len(old_lines)):
            l = old_lines[i]
            ln = len(l)
            ln -= 5*l.count('\u')
            ln -= 3*l.count('\\x')
            space = (max_line - ln)/2
            old_lines_cent.append(''.join([' ']*space)+l+''.join([' ']*space))
            
        new_string = '\\n'.join(old_lines_cent)
        line = line.replace(old_string, new_string)

        #append other properties:
        line = '\n'.join(["    wrapWidth=2.0, bold=True, font='Courier',", line])


    #Set duration constants
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
