#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random, time, pickle, os.path
from analysis import analysis_logging as logger
import numpy as np
from scipy.signal import hamming

LOGGER = logger.get_logger("csp_bci_analysis", "info")

class CspBCIAnalysis(object):
    def __init__(self, send_func):
        self.send_func = send_func
        self.last_time = time.time()

    def get_requested_configs(self):
        """Define config we wish to get. For instance, lets request
        for Freqs config, that is a string like '1 2 10 20'
        indicationg DIODE frequencies. In SSVEP paradigm this config is essential for:
        - determine 'which frequencies to look for'
        - determine which decision we can make (by default decision from 0 to len(Freqs)
        """
        return ['Freqs','SamplingRate', 'SaveFileName','SaveFilePath']

    def set_configs(self, configs):
        """Fired just after get_requested_configs is called and just before
        first call to .analyse()."""
        self.fs = int(configs['SamplingRate'])
        allFreqs = [int(i) for i in configs['Freqs'].split(' ')]

        self.indexMap = {}
        for i in range(len(allFreqs)):
            if allFreqs[i] != 0:
                self.indexMap[allFreqs[i]] = i
        self.freqs = self.indexMap.keys()

        LOGGER.info("Have freqs:")
        LOGGER.info(str(self.freqs))
        LOGGER.info("indexMap:")
        LOGGER.info(str(self.indexMap))

        #get stats from file
        file_name = os.path.normpath(os.path.join(
               configs['SaveFilePath'], configs['SaveFileName']))
        csp_file = file_name+'.csp'
        f = open(csp_file, 'r')
        d = pickle.load(f)
        f.close()
        LOGGER.info("Got csp config:")
        LOGGER.info(str(d))

        self.value = d['value']
        self.mu = d['mu']
        self.sigma = d['sigma']
        self.q = d['q']

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

        csp_sig = np.dot(self.q.P[:,0], data[:-3,:])#dostajemy jeden kanał o zadanej długości
        csp_sig -= csp_sig.mean()#normujemy
        csp_sig /= np.sqrt(np.sum(csp_sig*csp_sig))#normujemy
        freq, feeds = self._analyse(csp_sig)
        LOGGER.info("Got feeds: "+str(feeds))
        if freq > 0:
            self.send_func(self.indexMap[freq])
        else:
            LOGGER.info("Got 0 freq - no decision")


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
        fs, freqs, value, mu, sigma = self.fs, self.freqs, self.value, self.mu, self.sigma
        N = len(signal)
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
        return result, zscores
                    
