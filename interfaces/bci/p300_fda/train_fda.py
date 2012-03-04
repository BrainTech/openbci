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

#~ filename = 'tomek2_p300.obci'
#~ CHANNELS = ['O1','O2','Cz','Pz','T5','T6','FCz','Fz']
fn = "ania_d_1_train.obci"
fPath = os.path.join('dane',"ania_dla_mnie")
filename = os.path.join(fPath, fn)

csp_time = [0.25,0.75]
pVal = 0.99
nRepeat = 3
avrM = 8
conN = 2

# Extracts signal data
data = sp.signalParser(filename)
Fs = data.getSamplingFrequency()

CHANNELS = data.getChannelList()

chL = len(CHANNELS)
use_channels = ";".join(CHANNELS)

Signal = data.getData(CHANNELS)
#~ data.setMontage(montage)

# Get tags
trgTags = data.get_p300_tags() # target tags
ntrgTags = data.get_not_p300_tags()
trialTags = data.getTrialTags()

# Set filter
filtr = Filtr(Fs)


######################################
#~ ## SIGNAL  PREPARATION
#~ MONTAGE = 0.5*(Signal[-1]+Signal[-2])
######################################
## SIGNAL  PREPARATION
MONTAGE = Signal.mean(axis=0)
SIGNAL = Signal - MONTAGE
print SIGNAL.shape

#~ 
#~ SIGNAL = np.zeros(MONTAGE.shape[0])
#~ for C in xrange(chL):
    #~ s = Signal[C] - MONTAGE
    #~ s = filtr.filtrHigh(s)
    #~ s = filtr.filtrLow(s)
    #~ Signal[C] = s
    #~ print s.shape
    #~ SIGNAL = np.vstack( (SIGNAL, s))
#~ 
#~ SIGNAL = SIGNAL[1:]
print SIGNAL.shape
p300 = P300_train(CHANNELS, Fs, avrM, conN, csp_time)
p300.trainClassifier(SIGNAL, trgTags, ntrgTags)

if p300.isClassifiedFDA():
    print "FDA Classified SUCCESS!"
    P, w, c = p300.getPWC()
    
# Configuration dict
cfg = {"csp_time":csp_time,
        "use_channels": use_channels,
        'pVal':pVal,
        'avrM':avrM,
        'conN':conN,
        "nRepeat":nRepeat,
        "P":P,
        "w":w,
        "c":c
        }


#~ p300 = P300_analysis(Fs, cfg)
#~ p300.setPWC(P, w, c)
#~ np.save( "./PWC/"+filename, np.array(P,w,c) )

# Saving config var to a file
conf = []
for key in cfg.keys():
    conf.append( "{0}={0}".format(key) )
exec( 'np.savez("./output_var/"+fn, {0})'.format(', '.join(conf)))

tags = data.get_all_tags()

sys.exit()

repeatArr = np.zeros(trialTags.shape[0])
CONTINUE = True

dPole = {}
for i in range(nRepeat): dPole[i] = np.zeros(8)

skutecznosc = 0
repeatArr = np.array([])
keys = np.array(tags.keys())


for epoch in range(trialTags.shape[0]):
    N = 0
    print "epoch: ", epoch

    nPole = np.zeros(8)
    #~ dValues = np.zeros(8)

    while(CONTINUE):
        
        np.random.shuffle(keys)
        n = np.random.randint(0, len(keys))
        t = keys[n]
        blink = tags[t]

        if nPole[blink] == 1:
            continue

        #~ time.sleep(0.2)
        s = SIGNAL[:, int(t):int(t)+Fs]
        end = p300.testData(s, blink)

        dPole[N][blink] = p300.getRecentD()
        print "na zewnatrz: "
        print "{0[0]:5.5} {0[1]:5.5} {0[2]:5.5} {0[3]:5.5}\n{0[4]:5.5} {0[5]:5.5} {0[6]:5.5} {0[7]:5.5}".format(dPole[N])

        nPole[blink] += 1
        #~ print "nPole: ", nPole
        
        if nPole.sum() == 8:
            nPole = np.zeros(8)
            N += 1

        
        if end != -1:
            dec = p300.getDecision()
            dValues = np.zeros(8)
            if dec == 1:
                skutecznosc += 1
            break

        if N == nRepeat+1:
            dec = p300.forceDecision()
            if dec == 1:
                skutecznosc += 1
                break           

    repeatArr = np.append(repeatArr, N)
    #~ for idx in range(N):
        #~ print "dPole[{0}]: ".format(idx),
        #~ print dPole[idx]
        #~ 
        #~ py.subplot(2,5,idx+1)
        #~ py.plot(dPole[idx],'r.')
        #~ py.title(idx)
#~ 
    #~ py.show()


print "skutecznosc = ", skutecznosc
py.plot(repeatArr)
py.show()            

