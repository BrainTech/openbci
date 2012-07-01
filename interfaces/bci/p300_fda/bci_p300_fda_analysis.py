#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random, time
from interfaces import interfaces_logging as logger
import numpy as np

from interfaces.bci.p300_fda.p300_fda import P300_analysis
from interfaces.bci.p300_fda.p300_draw import P300_draw
from signalAnalysis import DataAnalysis

LOGGER = logger.get_logger("bci_p300_fda_analysis", "info")
DEBUG = False

class BCIP300FdaAnalysis(object):
    def __init__(self, send_func, cfg, montage_matrix, sampling):
        
        self.send_func = send_func
        self.last_time = time.time()
        self.fs = sampling
        self.montage_matrix = montage_matrix

        self.nPole = np.zeros(8)
        self.nMin = cfg['nMin']
        self.nMax = cfg['nMax']
        nRepeat = cfg['nLast']

        csp_time = cfg['csp_time']
        self.pVal = float(cfg['pVal'])
        use_channels = cfg['use_channels']

        nRepeat = cfg['nRepeat']
        avrM = cfg['avrM']
        conN = cfg['conN']
        
        print "cfg['w']: ", cfg['w']
        self.p300 = P300_analysis(sampling, cfg, fields=8)
        self.p300.setPWC( cfg['P'], cfg['w'], cfg['c'])
        
        self.debugFlag = cfg['debug_flag']
        
        if self.debugFlag:
            self.p300_draw = P300_draw(self.fs)
            self.p300_draw.setTimeLine(conN, avrM, csp_time)
        
        self.epochNo = 0
        
        

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
        LOGGER.debug("Got data to analyse... after: "+str(time.time()-self.last_time))
        LOGGER.debug("first and last value: "+str(data[0][0])+" - "+str(data[0][-1]))
        self.last_time = time.time()
        #Wszystko dalej powinno się robić dla każdego nowego sygnału
        
        # Get's montaged signal
        signal = np.dot(self.montage_matrix.T, data)

        # Counts each blink
        self.nPole[blink.index] += 1

        # Classify each signal
        self.p300.testData(signal, blink.index)
        dec = -1

        # If statistical significanse
        if self.p300.isItEnought() != -1:
            dec = self.p300.getDecision()

        #~ if (dec == -1) and (self.nPole.min() == self.nMax):
            #~ dec = self.p300.forceDecision()

        print "dec: ", dec

        if dec != -1:
            LOGGER.info("Decision from P300: " +str(dec) )
            
            if self.debugFlag:
                self.p300_draw.savePlotsSignal(self.p300.getSignal(), 'signal_%i_%i.png' %(self.epochNo,dec) )
                self.p300_draw.savePlotsD(self.p300.getArrTotalD(), self.pVal, 'dVal_%i_%i.png' %(self.epochNo,dec))
            
            self.p300.newEpoch()
            self.epochNo += 1
            
            self.nPole = np.zeros( self.nPole.shape)
            
            self.send_func(dec)
        else:
            LOGGER.info("Got -1 ind- no decision")
