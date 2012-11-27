#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random, time, pickle, os.path
import numpy as np
from scipy.signal import hamming
import scipy.stats as st
from obci_utils import context as ctx

DEBUG = False

class BCISsvepCspAnalysis(object):
    def __init__(self, send_func, freqs, cfg, montage_matrix, sampling, 
                 context=ctx.get_dummy_context('BCISsvepCspAnalysis')):
        self.logger = context['logger']
        self.send_func = send_func
        self.last_time = time.time()
        self.fs = sampling
        self.montage_matrix = montage_matrix
        allFreqs = freqs

        self.indexMap = {}
        k = 0
        for i in range(len(allFreqs)):
            if allFreqs[i] != 0:
                self.indexMap[allFreqs[i]] = k
                k += 1
        self.freqs = self.indexMap.keys()

        self.logger.info("Have freqs:")
        self.logger.info(str(self.freqs))
        self.logger.info("indexMap:")
        self.logger.info(str(self.indexMap))


        self.value = cfg['value']
        self.mu = cfg['mu']
        self.sigma = cfg['sigma']
        self.q = cfg['q']
        self.out_top = cfg['out_top']
        self.out_bottom = cfg['out_bottom']

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
        self.logger.debug("Got data to analyse... after: "+str(time.time()-self.last_time))
        self.logger.debug("first and last value: "+str(data[0][0])+" - "+str(data[0][-1]))
        self.last_time = time.time()
        #print("P: "+str(self.q.P[:,0].shape))
        #print("montage: "+str(self.montage_matrix.shape))
        #print("data: "+str(data.shape))
        #print("montage X data: "+str(np.dot(self.montage_matrix, data).shape))
        csp_sig = np.dot(self.q.P[:,0], np.dot(self.montage_matrix.T, data))
        csp_sig -= csp_sig.mean()#normujemy
        csp_sig /= np.sqrt(np.sum(csp_sig*csp_sig))#normujemy
        freq, feeds = self._analyse(csp_sig)
        self.logger.info("Got feeds: "+str(feeds)+" and freq: "+str(freq))
        if DEBUG:
            if random.random() > 0.5:
                freq = random.choice(self.indexMap.keys())
        if freq > 0:
            self.send_func(self.indexMap[freq])
        else:
            self.logger.info("Got 0 freq - no decision")


    def _analyse(self, signal):
        """This function performs classification based on correlations
        
        Parameters:
        ===========
        signal : 1darray
        signal to be analyzed. It is one dimensional, so probably needs to be
        spatialy filtered first.
        fs : int
        sampling frequency in Hz
        freqs : list
        frequencies to be detected in signal
        value : float
        a treshold value, above which detection will be positive
        mu : float
        a mean value of test distribution (for Z-scoring)
        sigma : float
        a standard deviation of test distribution (for Z-scoring)
        
        Returns:
        ========
        result : float or 0
        if there was successful detection, selected frequency will be returned.
        In other case, 0 is returned.
        """
        sig = signal
        fs, freqs, value, mu, sigma, out_top, out_bottom = self.fs, self.freqs, self.value, self.mu, self.sigma, self.out_top, self.out_bottom
        N = len(signal)
        if sig.min() < out_bottom or sig.max() > out_top:
            return 0, []

        T = N / float(fs)
        t_vec = np.linspace(0, T, N)
        max_lag = int(0.1 * fs)
        sig = signal /  np.sqrt(np.sum(signal * signal))
        result = 0
        mx_old = 0
        zscores = []
        for f in freqs:
            sin = np.sin(2*np.pi*t_vec*f)
            sin /= np.sqrt(np.sum(sin * sin))
            xcor = np.correlate(sig, sin, 'full')[N - 1 - max_lag:N+max_lag]
            mx = (np.max(xcor) - mu)/sigma
            zscores.append(mx)
            if mx > value:
                if mx > mx_old:
                    result = f
                    mx_old = mx
        if result > 0:
            q1 = st.scoreatpercentile(zscores, 25)
            q2 = st.scoreatpercentile(zscores, 50)
            q3 = st.scoreatpercentile(zscores, 75)
            iqr = abs(q1 - q3)
            if mx_old <= q2 + 1.5*iqr:
                result = 0

        return result, zscores
                    
