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
"""Holds experiment builder config"""



#A complicated constant. Don't change it.
USE_MULTIPLEXER = True      

CONFIG = {}

#Set this to true if you want shuffled packages and screens in packages
CONFIG['shuffle'] = True


#Set screens to be shown, divided into packages. Each package is determined 
#by one list of strings representing relative path to ugm config file
#located in openbci/ugm/config/ directory.
CONFIG['screens'] = [
        ['ania/mk-mo', 'ania/sk-mo', 'ania/dk-mo'],
        ['zosia/wiel1', 'zosia/wiel2', 'zosia/wiel3', 'zosia/wiel4']
]


#Set diode frequencies for every screen. Structure of 'freqs' should be
#the same as structure of 'screens'
CONFIG['freqs'] = [
    [
        [70, 12, 15, 70, 70, 13, 14, 70], # 'ania/mk-mo'
        [70, 12, 15, 70, 70, 13, 14, 70], # 'ania/sk-mo'
        [70, 12, 15, 70, 70, 13, 14, 70]], # etc....
    [
        [70, 12, 15, 70, 70, 13, 14, 70],  # 'zosia/wiel1'
        [70, 12, 15, 70, 70, 13, 14, 70],  # 'zosia/wiel2'
        [70, 12, 15, 70, 70, 13, 14, 70], # ...
        [70, 12, 15, 70, 70, 13, 14, 70]]
        ]

#Set delay for every screen. Use intiger to set constant delay for every screen.
#Use tuple eg. (2, 5) to set random delay between two numbers.
#Delay is in seconds
#CONFIG['delay'] = (2, 5)
CONFIG['delay'] = 3


#Define how many repeaded cycles from one package should be presented.
#Eg. having 'packages' = [['x','y'],['a','b','c']] and repeats = 3
#(and 'shuffle' = False)  you'll get subsequent sequence of screens:
# x,y,x,y,x,y,a,b,c,a,b,c,a,b,c
#when repeats = 1 you'll get:
# x,y,a,b,c
CONFIG['repeats'] = 5


#Set readable descriptions for every config file
#Those descriptions will be visible in tags
CONFIG['readable_names'] = {
    'ania/mk-mo' : 'murr',
    'ania/sk-mo' : 'surr',
    'ania/dk-mo' : 'durr',
    'zosia/wiel1' : 'w1rr',
    'zosia/wiel2' : 'w2rr',
    'zosia/wiel3' : 'w3rr',
    'zosia/wiel4' : 'w4rr',
}

# set this to True and set DEFAULT_FREQS to use one frequencies set for all
# screens. Then you can omit defining CONFIG['freqs']
CONFIG['use_default_freqs'] = True
CONFIG['default_freqs'] = [70, 12, 15, 70, 70, 13, 14, 70]


#Set this to True if you want to have breaks between packages.
#What happens during the break is defined below.
CONFIG['make_package_breaks'] = True
#Set break duration in seconds
CONFIG['break_package_len'] = 3
#Set break screen (in format as in 'screens')
CONFIG['break_package_screen'] = 'black'
#Set dides frequencies for the break
CONFIG['break_package_freqs'] = [70, 70, 70, 70, 70, 70, 70, 70]


#Set this to True if you want to have breaks between screens.
#What happens during the break is defined below.
CONFIG['make_screen_breaks'] = True
#Set break duration in seconds
CONFIG['break_screen_len'] = 3
#Set break screen (in format as in 'screens')
CONFIG['break_screen_screen'] = 'black'
#Set dides frequencies for the break
CONFIG['break_screen_freqs'] = [70, 70, 70, 70, 70, 70, 70, 70]



#Set welcoming screen (in format as in 'screens')
CONFIG['hi_screen'] = 'hi_screen'
#Set welcoming screen duration (in seconds)
CONFIG['hi_screen_delay'] = 3
#Set ending screen (in format as in 'screens')
CONFIG['bye_screen'] = 'bye_screen'
#Set ending screen duration (in seconds)
CONFIG['bye_screen_delay'] = 3


#Set a list of sounds played before every screen.
#Sounds are played in a cycle, eg having 'sound' = ['a.wav', 'b.wav', 'c.wav']
#and first 5 screens like q,w,e,r,t you'll get 
#subsequend pairs screen -> sound:
# q -> a.wav, w ->b.wav, e->c.wav, r->a.wav, t->b.wav
#
#Format of the sound -> a path to the sound starting from 
#openbci/experiment_builder directory
#CONFIG['sounds'] = ['resources/ping.wav', 'resources/ping.wav',
#                    'resources/ping.wav', 'resources/ping.wav']
