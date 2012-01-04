# -*- coding: utf-8 -*-
#!/usr/bin/env python

#Set this to true if you want shuffled packages and screens in packages
import random, copy
shuffle = True

#Set frequencies to be part of the experiment
f1 = [15, 17, 19, 25]#range(15, 17)#15,...,24
f2 = [15, 17, 19, 25]
f3 = [13, 15, 17, 19,
      21, 23, 25, 27]
#Set screens to be shown, divided into packages. Each package is determined 
#by one list of strings representing relative path to ugm config file
#located in openbci/ugm/config/ directory.
screens = [
    ['fields1']*len(f1),
    ['fields4']*len(f2),
    ['fields8']*len(f3)
    ]

#Set diode frequencies for every screen. Structure of 'freqs' should be
#the same as structure of 'screens'
freqs = [
      [],
      [],
      []
      ]
#f1
for i, fr in enumerate(f1):
    diodes = [0]*8
    diodes[1] = fr
    freqs[0].append(diodes)
    # like [ [0,15,0,0,0,0,0,0], [0,16,..... , [0,24,0,0,0,0,0,0] ]

#f2
for i, fr in enumerate(f2):
    diodes = [0]*8
    diodes[1] = fr
    f22 = list(f2)
    f22.remove(fr)
    random.shuffle(f22)
    diodes[2] = f22[0]
    diodes[5] = f22[1]
    diodes[6] = f22[2]
    freqs[1].append(diodes)

#f3
for i, fr in enumerate(f3):
    diodes = [0]*8
    diodes[1] = fr
    f33 = list(f3)
    f33.remove(fr)
    random.shuffle(f33)
    for i in range(6):
        diodes[i+2] = f33[i]
    diodes[0] = f33[-1]
    diodes[1] = fr
    freqs[2].append(diodes)

BBB = 2
for i in range(BBB-1):
    screens.append(copy.deepcopy(screens[0]))
    freqs.append(copy.deepcopy(freqs[0]))
    screens.append(copy.deepcopy(screens[1]))
    freqs.append(copy.deepcopy(freqs[1]))
    screens.append(copy.deepcopy(screens[2]))
    freqs.append(copy.deepcopy(freqs[2]))
#Set delay for every screen. Use intiger to set constant delay for every screen.
#Use tuple eg. (2, 5) to set random delay between two numbers.
#Delay is in seconds
#CONFIG['delay'] = (2, 5)
delay = 1

#Define how many repeaded cycles from one package should be presented.
#Eg. having 'packages' = [['x','y'],['a','b','c']] and repeats = 3
#(and 'shuffle' = False)  you'll get subsequent sequence of screens:
# x,y,x,y,x,y,a,b,c,a,b,c,a,b,c
#when repeats = 1 you'll get:
# x,y,a,b,c
repeats = [1, 1, 1]*BBB

#Set readable descriptions for every config file
#Those descriptions will be visible in tags
readable_names = { 'fields1' : 'fields1',
                   'fields4' : 'fields4',
                   'fields8' : 'fields8',
                   }

# set this to True and set DEFAULT_FREQS to use one frequencies set for all
# screens. Then you can omit defining CONFIG['freqs']
use_default_freqs = False
default_freqs = [70, 12, 15, 70, 70, 13, 14, 70]

#Set this to True if you want to have breaks between packages.
#What happens during the break is defined below.
make_package_breaks = True

#Set break duration in seconds
break_package_lens = [1,
                      1, 1, 1,
                      1, 1
                      ]

#Set break screen (in format as in 'screens')
break_package_screens = ['text_neg_10s', 
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


