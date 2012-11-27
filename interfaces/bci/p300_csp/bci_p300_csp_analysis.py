#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random, time, pickle, os.path
import numpy as np
import scipy.signal as ss
from scipy.signal import hamming
from analysis.csp.filtfilt import filtfilt
from analysis.csp.artifactClassifier import artifactsClasifier
import p300
from obci_utils import context as ctx

DEBUG = False

class BCIP300CspAnalysis(object):
    def __init__(self, send_func, cfg, montage_matrix, sampling,
                 context=ctx.get_dummy_context('BCIP300CspAnalysis')):
        self.logger = context['logger']
        self.send_func = send_func
        self.last_time = time.time()
        self.fs = sampling
        self.montage_matrix = montage_matrix

        self.q = cfg['q']
        self.treshold = cfg['treshold']
        self.a_features = cfg['a_features']
        self.bands = cfg['bands']
        #self.analyze = p300.p300analysis(cfg['targets'], cfg['non_targets'], cfg['mean'], cfg['mu'], cfg['sigma'], cfg['left'], cfg['right'])
        self.analyze = p300.p300analysis2(cfg['cl'], self.q.P, 2, cfg['mean'], cfg['mu'], cfg['sigma'], cfg['left'], cfg['right'])
        self.b, self.a = ss.butter(3, 2*1.0/self.fs, btype='high')
        self.b_l, self.a_l = ss.butter(3, 2*20.0/self.fs, btype='low')


    def analyse(self, blink, data):
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
        self.logger.debug("DATA SIZE: "+str(data.shape))
        self.logger.debug("BLINK index / ts / real_ts: "+str(blink.index)+" / "+str(blink.timestamp)+" / "+str(time.time()))
        self.last_time = time.time()
        #Wszystko dalej powinno się robić dla każdego nowego sygnału
        signal = np.dot(self.montage_matrix.T, data)                      
        self.logger.debug("AFTER MONTAGE SIGNAL SIZE: "+str(signal.shape))
        tmp_sig = np.zeros(signal.shape)
        for e in xrange(len(self.montage_matrix.T)):
            tmp = filtfilt(self.b,self.a, signal[e, :])
            tmp_sig[e, :] = filtfilt(self.b_l, self.a_l, tmp)
        
        if artifactsClasifier(tmp_sig, self.a_features, self.bands, self.fs):
            #2 Montujemy CSP
            #sig = np.dot(self.q.P[:, 0], tmp_sig)

            #3 Klasyfikacja: indeks pola albo -1, gdy nie ma detekcji
            ix = self.analyze.analyze(tmp_sig, blink.index, tr=self.treshold)
            if ix >= 0:
                self.send_func(ix)
            else:
                self.logger.info("Got -1 ind- no decision")
        else:
            self.logger.info("Got -1 ind- no decision")
