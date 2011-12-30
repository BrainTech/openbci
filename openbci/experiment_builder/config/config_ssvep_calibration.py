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
#      Łukasz Polak <l.polak@gmail.com>
#
#"""Holds experiment builder config"""


#Set this to true if you want shuffled packages and screens in packages



#[experiment]
shuffle = True


#Set screens to be shown, divided into packages. Each package is determined 
#by one list of strings representing relative path to ugm config file
#located in openbci/ugm/config/ directory.


f = range(15, 25)#15,...,24

screens = [['text']*len(f)]

#Set diode frequencies for every screen. Structure of 'freqs' should be
#the same as structure of 'screens'
freqs = [
      [[0]*8]*len(f)
	]

for i, fr in enumerate(f):
    freqs[0][i][1] = fr

#Set delay for every screen. Use intiger to set constant delay for every screen.
#Use tuple eg. (2, 5) to set random delay between two numbers.
#Delay is in seconds
#CONFIG['delay'] = (2, 5)
delay = 3


#Define how many repeaded cycles from one package should be presented.
#Eg. having 'packages' = [['x','y'],['a','b','c']] and repeats = 3
#(and 'shuffle' = False)  you'll get subsequent sequence of screens:
# x,y,x,y,x,y,a,b,c,a,b,c,a,b,c
#when repeats = 1 you'll get:
# x,y,a,b,c
repeats = 100


#Set readable descriptions for every config file
#Those descriptions will be visible in tags
#readable_names = { 'ania/mk-mo' : 'murr', 'ania/sk-mo' : 'surr','ania/dk-mo' : 'durr',  'zosia/wiel1' : 'w1rr',  'zosia/wiel2' : 'w2rr',    'zosia/wiel3' : 'w3rr',    'zosia/wiel4' : 'w4rr',}
readable_names = { 'text' : 'field1', 'text_neg': 'field2' }

# set this to True and set DEFAULT_FREQS to use one frequencies set for all
# screens. Then you can omit defining CONFIG['freqs']
use_default_freqs = False
default_freqs = [70, 12, 15, 70, 70, 13, 14, 70]


#Set this to True if you want to have breaks between packages.
#What happens during the break is defined below.
make_package_breaks = True
#Set break duration in seconds
break_package_len = 60
#Set break screen (in format as in 'screens')
break_package_screen = 'black'
#Set dides frequencies for the break
break_package_freqs = [-1,0,0,0,0,0,0,0]


#Set this to True if you want to have breaks between screens.
#What happens during the break is defined below.
make_screen_breaks = True
#Set break duration in seconds
break_screen_len = 1
#Set break screen (in format as in 'screens')
break_screen_screen = 'black'
#Set dides frequencies for the break
break_screen_freqs = [-1, 0, 0, 0, 0, 0, 0, 0]



#Set welcoming screen (in format as in 'screens')
hi_screen = ''
#Set welcoming screen duration (in seconds)
hi_screen_delay = 0
#Set ending screen (in format as in 'screens')
bye_screen = 'bye_screen'
#Set ending screen duration (in seconds)
bye_screen_delay = 5


