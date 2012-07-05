
#!/usr/bin/python
# coding: UTF-8
import numpy as np
import pylab as py  

import scipy.io
import scipy.stats as st
import signalParser as sp
from signalAnalysis import DataAnalysis
from p300_fda import P300_train, P300_analysis
from p300_draw import P300_draw

import sys, os, time


fn = 'd_cabel_2.obci'
CHANNELS = ["O1","O2", "Fz", "C3", "Cz", "C4", "T7", "P3", "Pz", "P4", "T8", "O1", "O2"]
#~ CHANNELS = ["O1","O2", "Fz", "C3", "Cz", "C4", "P3", "Pz", "P4", "O1", "O2"]
montage = ["A1", "A2"]

fPath = os.path.join(r'/home/brain/dane_moje')

filename = os.path.join(fPath, fn)


# Extracts signal data
data = sp.signalParser(filename)
Fs = data.getSamplingFrequency()

#~ refData = data.getData(ref_ch).mean(axis=0)

data.setMontage(montage)
use_channels = ";".join(CHANNELS)

Signal = data.getData(CHANNELS)
print "Signal.shape: ",Signal.shape

chL = Signal.shape[0]
CHANNELS = ";".join(CHANNELS)

#######################################
# Extracting data
# Get tags
trgTags = data.get_p300_tags() # target tags
ntrgTags = data.get_not_p300_tags()
trialTags = data.getTrialTags()

sampleCount = Signal.shape[1]
trgTags = trgTags[trgTags<sampleCount-Fs]
ntrgTags = ntrgTags[ntrgTags<sampleCount-Fs]
trialTags = trialTags[trialTags<sampleCount-Fs]

# Get data
target, nontarget = data.getTargetNontarget(Signal, trgTags, ntrgTags)

######################################
#~ ## SIGNAL  PREPARATION
#~ MONTAGE = 0.5*(Signal[-1]+Signal[-2])
######################################
## SIGNAL  PREPARATION
MONTAGE = Signal.mean(axis=0)
SIGNAL = Signal - MONTAGE
print SIGNAL.shape

N = 0
d = {}
P_dict = {}
for avrM in [1]:
    #~ for conN in [1,2,3]:
    for conN in [1]:
        for csp_time in [0.1,0.15,0.2]:
            for dt in [0.5]:
            #~ for dt in [0.25]:
                d[N] = {"avrM":avrM, "conN":conN, "csp_time":[csp_time, csp_time+dt]}
                N += 1

#################################
## CROSS CHECKING
l = np.zeros(N)
for idxN in range(N):
    KEY = d[idxN].keys()
    for k in KEY:
        c = "{0} = {1}".format(k, d[idxN][k])
        print c
        exec(c)
        
    p300 = P300_train(CHANNELS, Fs, avrM, conN, csp_time)
    l[idxN] = 0
    for X in xrange(1):
        #~ l[idxN] += p300.crossCheck(SIGNAL, target, nontarget)
        l[idxN] += p300.valid_kGroups(SIGNAL, target, nontarget, 2)
    P_dict[idxN] = p300.getPWC()[0]
    
    
#################################
# Finding best    

print "\n"*5
length = len(l)
print "L: ", l
P, conN, avrM, csp_time = None, None, None, None
BEST = 0
arr = np.arange(length)
for i in range(5):
    bestN = int(arr[l==l.max()])
    print "best_{0}: {1}".format(i, bestN)
    print "d[bestN]: ", d[bestN]
    print "l[bestN]: ", l.max()
    if i == 0: BEST = bestN
    l[bestN] = l.min()-1


P = P_dict[BEST]
avrM = d[BEST]["avrM"]
conN = d[BEST]["conN"]
csp_time = d[BEST]["csp_time"]

## Plotting best
p300_draw = P300_draw()
p300_draw.setCalibration(target, nontarget, trgTags, ntrgTags)
p300_draw.setCSP(P)
p300_draw.setTimeLine(conN, avrM, csp_time)
p300_draw.plot()

sys.exit()

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

