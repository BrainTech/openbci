#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sample_bci_analysis
import random, time, numpy
import analysis_logging as logger
LOGGER = logger.get_logger("sample_bci_analysis", "info")

class SsvepBCIAnalysis(object):
    def __init__(self, send_func):
        self.send_func = send_func
        self.last_time = time.time()
        self.lastChoice = -2
        self.repCounter = 0
        self.ignoreCounter = 0

    def get_requested_configs(self):
        """Define config we wish to get. For instance, lets request
        for Freqs config, that is a string like '1 2 10 20'
        indicationg DIODE frequencies. In SSVEP paradigm this config is essential for:
        - determine 'which frequencies to look for'
        - determine which decision we can make (by default decision from 0 to len(Freqs)
        """
        return ['Freqs','SamplingRate', 'Borders']

    def set_configs(self, configs):
        """Fired just after get_requested_configs is called and just before
        first call to .analyse()."""
        self.repeats = 2
        self.ignores = 2
        allFreqs = [int(i) for i in configs['Freqs'].split(' ')]
        self.sampling_rate = int(configs['SamplingRate'])
        self.numOfFreq = len(allFreqs)
        self.indexMap = self.numOfFreq * [0]
        self.freqs = (self.numOfFreq * 3) * [0]
        self.borders = [float(b) for b in configs['Borders'].split(' ')]

        j = 0
        for i in range(self.numOfFreq):
            while (allFreqs[j] == 0):
                j += 1
            self.freqs[i] = allFreqs[j]
            self.indexMap[i] = j
            self.freqs[i + self.numOfFreq] = 2 * allFreqs[j]
            self.freqs[i + (2 * self.numOfFreq)] = 3 * allFreqs[j]
            j += 1


    def analyse(self, data):
        """Fired as often as defined in hashtable configuration:
        # Define from which moment in time (ago) we want to get samples (in seconds)
        'ANALYSIS_BUFFER_FROM':
        # Define how many samples we wish to analyse every tick (in seconds)
        'ANALYSIS_BUFFER_COUNT':
        # Define a tick duration (in seconds).
        'ANALYSIS_BUFFER_EVERY':
        # To SUMP UP - above default values (0.5, 0.4, 0.25) define that
        # every 0.25s we will get buffer of length 0.4s starting from a sample 
        # that we got 0.5s ago.
        # Some more typical example would be for values (0.5, 0.5 0.25). 
        # In that case, every 0.25 we would get buffer of samples from 0.5s ago till now.

        data format is determined by another hashtable configuration:
        # possible values are: 'PROTOBUF_SAMPLES', 'NUMPY_CHANNELS'
        # it indicates format of buffered data returned to analysis
        # NUMPY_CHANNELS is a numpy 2D array with data divided by channels
        # PROTOBUF_SAMPLES is a list of protobuf Sample() objects
        'ANALYSIS_BUFFER_RET_FORMAT'

        """
        LOGGER.debug("Got data to analyse... after: "+str(time.time()-self.last_time))
        LOGGER.debug("first and last value: "+str(data[0][0])+" - "+str(data[0][-1]))
        self.last_time = time.time()

        if self.ignoreCounter > 0:
            LOGGER.info("Got data but ignores on ignoreCounter: "+str(self.ignoreCounter))
            self.ignoreCounter -= 1
            return

        dec = self._analyse(data[0])
        if ((dec != -1) and (self.lastChoice == dec)):
            self.repCounter += 1
        else:
            self.lastChoice = dec
            self.repCounter = 0

        if (self.repCounter >= self.repeats):
            self.ignoreCounter = self.ignores
            self.send_func(self.indexMap[dec])
        #if dec < 2:
        #    self.send_func(dec)


    def _analyse(self, d):
        numOfFreq = self.numOfFreq
        mul = 2
        d = d[-int(self.sampling_rate * mul):]
	d = numpy.array(d) - numpy.average(numpy.array(d))  
        #d = d[-int(self.sampling_rate * (now - tt)):]
        #d.extend((window - now + tt) * [0])	
        d2 = abs(numpy.fft.fft(d))
        d2 = [x**2 for x in d2]
        d2[0] = 0
        d2[1] = 0
        j = len(d2)
        amplitudes = [0] * (numOfFreq * 3)
        otherAmplitudes = numOfFreq * [0]

        otherFreqs = (numOfFreq * 3) * [0]

        for i in range(numOfFreq):
            otherFreqs[i] = float(self.freqs[i]) + 0.5

        for i in range(numOfFreq):
            amplitudes[i] = d2[int(self.freqs[i] * mul)] - 0.5*(d2[int(self.freqs[i] * mul - 1)] + d2[self.freqs[i]* mul + 1]) \
            + d2[self.freqs[i + numOfFreq] * mul] - 0.5*(d2[self.freqs[i + numOfFreq] * mul - 1] +  d2[self.freqs[i + numOfFreq]* mul + 1]) \
            + d2[self.freqs[i + (numOfFreq * 2)] * mul] - 0.5*(d2[self.freqs[i + (numOfFreq * 2)] * mul - 1] + d2[self.freqs[i + (numOfFreq * 2)]* mul + 1]) 

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


        # ustawienie na -1, oznacza, ze nie rozpoznana byla zadna czestosc.
        freqIndex = -1

        if ((diffs[bestCandidate] - avgOtherDiffs > self.borders[self.indexMap[bestCandidate]] * stdOtherAmplitude) and (diffs[bestCandidate]>0.0)):
            freqIndex = bestCandidate
        
        return freqIndex
