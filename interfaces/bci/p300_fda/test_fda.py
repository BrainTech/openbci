#!/usr/bin/python
# coding: UTF-8
import numpy as np
import pylab as py  

import scipy.io
import scipy.stats as st
import signalParser as sp
from Filtr import Filtr
from p300_fda import P300_train, P300_analysis

import sys, os, time

fn = "ania_d_1_test.obci"
fPath = os.path.join('dane',"ania_dla_mnie")
filename = os.path.join(fPath, fn)

data = sp.signalParser(filename)
Fs = data.getSamplingFrequency()
CHANNELS = data.getChannelList()
chL = len(CHANNELS)

Signal = data.getData(CHANNELS)
#~ data.setMontage(montage)

filtr = Filtr(Fs)


######################################
## SIGNAL  PREPARATION
MONTAGE = Signal.mean(axis=0)
SIGNAL = Signal - MONTAGE
print SIGNAL.shape

######################################
# GET CONFING VALUE
FN = "train".join(fn.split('test'))
CFG = np.load( os.path.join( "output_var", FN+'.npz'))
P, w, c = CFG['P'], CFG['w'], CFG['c']
csp_time = CFG['csp_time']
pVal = CFG['pVal']
use_channels = CFG['use_channels']

nRepeat = CFG['nRepeat']
avrM = CFG['avrM']
conN = CFG['conN']
CONTINUE = True

cfg = {"csp_time":csp_time,
        "use_channels": ";".join(CHANNELS),
        'pVal':pVal,
        'avrM':avrM,
        'conN':conN,
        "nRepeat":nRepeat
        }

zVal = st.norm.ppf(pVal)
nMax = 5
######################################
# Define arrays

dPole = {}
for i in range(nRepeat): dPole[i] = np.zeros(8)

skutecznosc = 0


######################################
## Set P300
p300 = P300_analysis(Fs, cfg)
p300.setPWC(P, w, c)

# Get tags
tags = data.get_all_tags()
trialTags = data.getTrialTags()
timeTags = tags.keys()



#############################################################            


#~ for epoch in range(10):
for epoch in range(10):
    print "epoch: ", epoch

    nPole = np.zeros(8)
    p300.newEpoch()
    
    np.random.shuffle(timeTags)

    for tag in timeTags:
        
        # 
        blink, t = tags[tag], tag
        nPole[blink] += 1
        
        # Analyse signal
        s = SIGNAL[:, int(t):int(t)+Fs]
        p300.testData(s, blink)
    
        if p300.isItEnought() != -1:
            dec = p300.getDecision()
            if dec == int(1):
                skutecznosc += 1            
            break
        
        if nPole.min() == nMax:
            dec = p300.forceDecision()
            if dec == int(1):
                skutecznosc += 1
                
        #~ print "na zewnatrz: "
        print "ostatnie d: ", p300.getRecentD()
        
        #~ print "nPole: ", nPole
            
    if dec != -1:
        print "wybrano -- {0}  | powinno byc {1}".format(dec, 1)    
    else:
        print "Nie wybrano  | powinno byc {1}".format(dec, 1)    

    dArrTotal = p300.getArrTotalD()
    minN = 10
    for i in range(8): 
        if len(dArrTotal[i]) < minN: minN = len(dArrTotal[i])
    #~ print "minN: ", minN
    
    #~ print "nPole.max(): ", nPole.max()
    #~ print "nPole.max(): ", int(nPole.max())

    for count in range(minN):
        m, yMinArr, yMaxArr = [],[],[]
        std = []
        py.subplot(2,5,count+1)

        tmpD = np.zeros(8)
        for pole in range(8):
            tmpD[pole] = dArrTotal[pole][:count+1].mean()
        
        for pole in range(8):
            tmpArr = np.delete(tmpD, pole)
            mVal = tmpArr.mean()
            stdVal = tmpArr.std()

            #~ print "tmpArr: ", tmpArr
            #~ print "mVal: ", mVal

            m.append(mVal)
            yMinArr.append(mVal-stdVal*zVal)
            yMaxArr.append(mVal+stdVal*zVal)
            
            #~ print dArrTotal[pole][count], " ",

            #~ print 

            py.plot(tmpD,'r.')
            
        print "m: ", m
        py.plot(m,'bo')
        
        yMin, yMax = tmpD.min(), tmpD.max()
        yMin, yMax = yMin-(yMax-yMin)*0.1, yMax+(yMax-yMin)*0.1
        py.title(count+1)
        py.ylim((yMin, yMax))
        py.xlim((-1,8))
        ySpan = yMax-yMin        

        for i in range(8):
            py.axvline(x=i, ymin=(m[i]-yMin)/ySpan, ymax=(yMaxArr[i]-yMin)/ySpan)
            #~ py.axvline(x=i, ymin=(yMinArr[i]-yMin)/ySpan, ymax=(yMaxArr[i]-yMin)/ySpan)

    py.show()


print "skutecznosc = ", skutecznosc
