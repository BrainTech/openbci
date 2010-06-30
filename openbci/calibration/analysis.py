import numpy as np
import os
import time
import sys
import random
import variables_pb2
import matplotlib.pyplot as plt
import math
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client
from operator import setitem


#def distinct(l):
#    d = {}
#    map(setitem, (d,)*len(l), l, [])
#    return d.keys()
def distinct(l):
    return list(set(l))
"""
d - array of signal values (one channel)
freqs - array of frequencies which we want to see on spectrum
window - length of signal in seconds
sampling_rate

returns array of power of given frequencies
"""
def simple_analyse(d, freqs, window, sampling_rate):
    d2 = abs(np.fft.fft(d))
    d2 = [x*x for x in d2]
    d3 = []
#    if (len(freqs) > 0):
    freqs = distinct(freqs)
    for i in freqs:
        d3.append(d2[int(i) * window])
    print "d3 ",d3
    return d3


def draw_spectrum(d, freqs, window, sampling_rate):
	amplitudes = simple_analyse(d, freqs, window, sampling_rate)
	t = np.arange(len(freqs))
	plt.plot(t,amplitudes)    

"""
d - signal values array, single channel 
window - d contains window * sampling_rate values
sampling_rate - 
numOfFreq - number of stimulation frequencies
returns array of differencies between standard deviations of given freqeuncies and average standard deviation of "other" frequencies
"""

def stat_analyse(d, numOfFreq, window, freqs, sampling_rate):

    mul = window
    d = d[-int(sampling_rate * mul):]
    #d = d[-int(sampling_rate * (now - tt)):]
    #d.extend((window - now + tt) * [0])	
    d2 = abs(np.fft.fft(d))
    d2 = [x**2 for x in d2]
    d2[0] = 0
    d2[1] = 0
    j = len(d2)
    amplitudes = [0] * (numOfFreq * 3)
    otherAmplitudes = numOfFreq * [0]

    freqs_new = (numOfFreq * 3) * [0]
    for i in range(numOfFreq):
        freqs_new[i] = freqs[i]
        freqs_new[i + numOfFreq] = 2 * freqs[i]
        freqs_new[i + (2 * numOfFreq)] = 3 * freqs[i]
        
    freqs = list(freqs_new)


    otherFreqs = (numOfFreq * 3) * [0]
    print "numOfFreq ", numOfFreq, "len(d2) ", len(d2), " int(freqs[i + (numOfFreq * 2)] * mul) ", int(freqs[i + (numOfFreq * 2)] * mul), "freqs ", freqs
    for i in range(numOfFreq):
        otherFreqs[i] = float(freqs[i]) + 0.5
    print "len freqs: ", len(freqs), " numOfFreq ", numOfFreq, "len \
            otherFreqs: ", len(otherFreqs)
    for i in range(numOfFreq):
        amplitudes[i] = d2[int(freqs[i] * mul)] - 0.5*(d2[int(freqs[i] * mul - 1)] + d2[int(freqs[i]* mul + 1)]) \
                + d2[int(freqs[i + numOfFreq] * mul)] - 0.5*(d2[int(freqs[i + numOfFreq] * mul - 1)] +  d2[int(freqs[i + numOfFreq]* mul + 1)]) \
                + d2[int(freqs[i + (numOfFreq * 2)] * mul)] - 0.5*(d2[int(freqs[i + (numOfFreq * 2)] * mul) - 1] + d2[int(freqs[i + (numOfFreq * 2)]* mul + 1)]) 

        otherAmplitudes[i] = d2[int(otherFreqs[i] * mul)] - 0.5*(d2[int(otherFreqs[i] * mul - 1)] + d2[int(otherFreqs[i] * mul + 1)])\
                + d2[int(otherFreqs[i + numOfFreq] * mul)] - 0.5*(d2[int(otherFreqs[i + numOfFreq] * mul - 1)] + d2[int(otherFreqs[i + numOfFreq]* mul + 1)])\
                + d2[int(otherFreqs[i + (numOfFreq * 2)] * mul)] - 0.5*(d2[int(otherFreqs[i + (numOfFreq * 2)] * mul - 1)] + d2[int(otherFreqs[i + (numOfFreq * 2)]* mul + 1)]) 

    
    avgAmplitude = 0.0
    avgOtherAmplitude = 0.0

    for i in range(numOfFreq):
        avgAmplitude +=  amplitudes[i]
        avgOtherAmplitude += otherAmplitudes[i]
    avgAmplitude /= float(numOfFreq)
    avgOtherAmplitude /= float(numOfFreq)

    stdAmplitude = 0.0
    stdOtherAmplitude = 0.0		
    diffs = numOfFreq * [0.0]
    otherDiffs = numOfFreq * [0.0]		

    avgs = numOfFreq * [0.0]
    otherAvgs = numOfFreq * [0.0]

    for i in range(numOfFreq):
        avgs[i] = ((avgAmplitude * numOfFreq) - amplitudes[i]) / float(numOfFreq - 1)	
        otherAvgs[i] = ((avgOtherAmplitude * numOfFreq) - otherAmplitudes[i]) / float(numOfFreq - 1)	

    for i in range(numOfFreq):
        diffs[i] = amplitudes[i] - avgs[i]
        otherDiffs[i] = otherAmplitudes[i] - otherAvgs[i]

        
    sumOtherDiffs = 0.0
   
    for i in range(numOfFreq):
        sumOtherDiffs += otherDiffs[i]

    avgOtherDiffs = float(sumOtherDiffs/numOfFreq)

    bestCandidate = 0

    for i in range(numOfFreq):
        if (diffs[bestCandidate] < diffs[i]):
            bestCandidate = i

    for i in range(numOfFreq):
        stdAmplitude += (amplitudes[i]-avgs[i])**2
        stdOtherAmplitude += (otherAmplitudes[i]-otherAvgs[i])**2

    stdAmplitude = (stdAmplitude/float(numOfFreq-1))**0.5
    stdOtherAmplitude = (stdOtherAmplitude/float(numOfFreq-1))**0.5


    return [x - avgOtherDiffs for x in diffs]


"""
zwraca tablice odchylen dla kazdej czestosci, rysowane na wykresie maja byc odchylenia kazdej czestosci innym kolorem
"""

#def diffs(d, freqs, ):


"""
d -- array of samples 
f -- array of frequencies
t -- array of timestamps of samples
tags -- array of timestamps of signal changes

n - number of seconds how long one frequency was presented

sr- sampling rate

min_freq

"""

def prepeare_signal_round_i(d, n, sr, min_freq, f):
    avg = sr * n * [0]
    amplitudes = len(f) * [0] 
    i = 0
    f2 = list(f)
    f2.sort()
    poz = {}
    for i in range(len(f2)):
        poz[f2[i]] = i 

    while (len(d) > 0) and (i/2 < len(f)):
        if (i%2 == 1):
            avg = [avg[i] + d[i] for i in range(sr * n)]
	#print "f[i] ", f[i], " min_freq ",min_freq, "f ", f
	#f
        #amplitudes[f[i] - min_freq] = simple_analyse(d, [f[i]], n, sr)[0]            
	else:
	    amplitudes[poz[f[i/2]]] = simple_analyse(d, [f[i/2]], n, sr)[0]            

        d = d[(sr * n) :]
        i += 1
    avg = [x/float(len(f)) for x in avg] 
   
    avg = simple_analyse(avg, f2, n, sr)
    return avg, amplitudes   

def draw_plots_round_i(d, n, sr, min_freq, f):
    d1, d2 = prepeare_signal_round_i(d, n, sr, min_freq, f)
    t1 = np.arange(len(d1))
    t2 = np.arange(len(d2))
    plt.plot(t1, d1, 'g', t2, d2, 'b')
    plt.show()


def draw_plots_round_ii(d, numOfFreqs, window, freqs, sampling_rate):
    
    diffs_per_freq = numOfFreqs * [numOfFreqs * [0]]
    
    t = np.arange((sampling_rate * window))
    f2 = list(freqs)
    f2.sort()
    poz = {}
    for i in range(len(f2)):
        poz[f2[i]] = i
    i = 0
    t = np.arange(len(freqs))
    while (len(d) > 0)and(i<len(freqs)):
        res = stat_analyse(d, numOfFreqs, window, freqs, sampling_rate)
        diffs_per_freq[poz[freqs[i]]] = res

        i += 1
        d = d[(sampling_rate * window):]
        plt.plot(t, res)   
    

    plt.show()
#    return diffs_per_freq


"""

extracts from vector of data and vector of tags, vector of exactly the data we need and vector of frequencies used

"""

def get_data(d, tags, numOfFreqs, n, sr):
    #data = variables_pb2.SampleVector()    
    i = 0
    start = 0
    f = []
    for x in tags.tags:
        if (x.name == "experiment_update"):
            if (start == 0):
                start = x.start_timestamp
            for y in x.desc.variables:
                if y.key == "Freqs":
                    f.append((int(y.value.split(",")[1])))  
      
    data = []
    for s in d.samples:
        if (s.timestamp >= start and s.timestamp <= start + numOfFreqs * n * sr):
            data.append(s.value)
    return data, f

def get_data_ii(d, tags, numOfFreqs, n, sr):
    #data = variables_pb2.SampleVector()    
    i = 0
    f = []
    for x in tags.tags:
        if (x.name == "experiment_update"):
            start = x.start_timestamp
            for y in x.desc.variables:
                if y.key == "Freqs":
                    f = [int(z) for z in (y.value.split(']'))[0].split('[')[1].split(',')]
                    f = f[:int(numOfFreqs)]  
                    print "GET_DATA_II  Freqs", f
      
    data = []
    for s in d.samples:
        if (s.timestamp >= start and s.timestamp <= start + numOfFreqs * n * sr):
            data.append(s.value)
    return data, f
    


def round1(d, tags, numOfFreqs,n,sr):

    d,f = get_data(d, tags, numOfFreqs,n,sr)
    print " f ", f
    min_freq = min(f)    
    draw_plots_round_i(d, n, sr, min_freq, f)

def round2(d, tags, numOfFreqs,n,sr):

    d,f = get_data_ii(d, tags, numOfFreqs,n,sr)
    print " f ", f
    min_freq = min(f)
    draw_plots_round_ii(d, numOfFreqs, n, f, sr)


#def draw_plots_round_ii()



#if __name__ == "__main__":

