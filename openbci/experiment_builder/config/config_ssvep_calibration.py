# -*- coding: utf-8 -*-
#!/usr/bin/env python

#Set this to true if you want shuffled packages and screens in packages
shuffle = True

#Set frequencies to be part of the experiment
f = range(15, 25)#15,...,24

#Set screens to be shown, divided into packages. Each package is determined 
#by one list of strings representing relative path to ugm config file
#located in openbci/ugm/config/ directory.
screens = [
    ['field1']*len(f),
    ['field1']*len(f),
    ['field1']*len(f)
    ]

#Set diode frequencies for every screen. Structure of 'freqs' should be
#the same as structure of 'screens'
freqs = [
      [],
      [],
      []
      ]
for j in range(len(freqs)):
    for i, fr in enumerate(f):
        diodes = [0]*8
        diodes[1] = fr
        freqs[j].append(diodes)
    # like [ [0,15,0,0,0,0,0,0], [0,16,..... , [0,24,0,0,0,0,0,0] ]

#Set delay for every screen. Use intiger to set constant delay for every screen.
#Use tuple eg. (2, 5) to set random delay between two numbers.
#Delay is in seconds
#CONFIG['delay'] = (2, 5)
delay = 2

#Define how many repeaded cycles from one package should be presented.
#Eg. having 'packages' = [['x','y'],['a','b','c']] and repeats = 3
#(and 'shuffle' = False)  you'll get subsequent sequence of screens:
# x,y,x,y,x,y,a,b,c,a,b,c,a,b,c
#when repeats = 1 you'll get:
# x,y,a,b,c
repeats = 1

#Set readable descriptions for every config file
#Those descriptions will be visible in tags
readable_names = { 'field1' : 'field1'}

# set this to True and set DEFAULT_FREQS to use one frequencies set for all
# screens. Then you can omit defining CONFIG['freqs']
use_default_freqs = False
default_freqs = [70, 12, 15, 70, 70, 13, 14, 70]

#Set this to True if you want to have breaks between packages.
#What happens during the break is defined below.
make_package_breaks = True

#Set break duration in seconds
break_package_lens = [30, 20, 5,
                      1, 1, 1,
                      1, 1
                      ]

#Set break screen (in format as in 'screens')
break_package_screens = ['text_neg_60s', 'text_neg_30s', 'text_neg_10s', 
                         'text_neg_5s', 'text_neg_4s', 'text_neg_3s', 
                         'text_neg_2s', 'text_neg_1s'] 

#Set dides frequencies for the break, -1 to turn off diodes
break_package_freqs = [-1,0,0,0,0,0,0,0]

#Set this to True if you want to have breaks between screens.
#What happens during the break is defined below.
make_screen_breaks = True

#Set break duration in seconds
break_screen_lens = [1]

#Set break screen (in format as in 'screens')
break_screen_screens = ['black']

#Set dides frequencies for the break
break_screen_freqs = [-1, 0, 0, 0, 0, 0, 0, 0]



#Set welcoming screen (in format as in 'screens')
hi_screens = ['text_neg_hi']
#Set welcoming screen duration (in seconds)
hi_screen_delays = [-1]
#Set ending screen (in format as in 'screens')
bye_screens = ['text_neg_bye']
#Set ending screen duration (in seconds)
bye_screen_delays = [-1]


