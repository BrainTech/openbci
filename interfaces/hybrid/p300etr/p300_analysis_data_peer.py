#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helps analyse data and sends it to decision making module.

Author: Dawid Laszuk
Contact: laszukdawid@gmail.com
"""

import random, time
from interfaces import interfaces_logging as logger
import numpy as np

from p300_fda import P300_analysis
from p300_draw import P300_draw
from signalAnalysis import DataAnalysis

LOGGER = logger.get_logger("p300_analysis_data_peer", "info")
DEBUG = False

class BCIP300FdaAnalysis(object):
    def __init__(self, send_func, cfg, montage_matrix, sampling):
        
        self.send_func = send_func
        self.last_time = time.time()
        self.fs = sampling
        self.montage_matrix = montage_matrix

        
        self.nMin = cfg['nMin']
        self.nMax = cfg['nMax']
        nLast = cfg['nLast']

        csp_time = cfg['csp_time']
        self.pVal = float(cfg['pVal'])
        use_channels = cfg['use_channels']

        avrM = cfg['avrM']
        conN = cfg['conN']
        
        self.cols = cfg['col_count']
        self.rows = cfg['row_count']
        self.nPole = np.zeros(self.cols+self.rows)

        self.epochNo = 0
        
        self.p300 = P300_analysis(sampling, cfg, rows=self.rows, cols=self.cols)
        self.p300.setPWC( cfg['P'], cfg['w'], cfg['c'])
        
        self.debugFlag = cfg['debug_flag']
        
        if self.debugFlag:
            self.p300_draw = P300_draw(self.fs)
            self.p300_draw.setTimeLine(conN, avrM, csp_time)
        
        
    def newEpoch(self):

        self.p300.newEpoch()
        self.epochNo += 1
        
        self.nPole = np.zeros( self.nPole.shape)
    

    def analyse(self, blink, data):
        """Fired as often as defined in hashtable configuration:
        # Define from which moment in time (ago) we want to get samples (in seconds)
        'ANALYSIS_BUFFER_FROM':"
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

        
        # Get's montaged signal
        signal = np.dot(self.montage_matrix.T, data)

        index = blink.index
        if int(index) >= self.cols: lineFlag, index = 'r', index - self.cols
        else:                       lineFlag = 'c'
        
        LOGGER.debug("Blink -- {0}*{1}".format(lineFlag, index))
        
        # Counts each blink
        self.nPole[blink.index] += 1
        LOGGER.debug("self.nPole: " + str(self.nPole))

        # Classify each signal
        self.p300.testData(signal, lineFlag, index)
        dec = -1

        if self.nPole.min() < self.nMin:
            return
        else:
            LOGGER.debug( "self.nPole: " + str(self.nPole) )
            pdf = self.p300.getProbabiltyDensity()
            
            if self.debugFlag:
                self.p300_draw.savePlotsSignal(self.p300.getSignal(), 'signal_%i_%i.png' %(self.epochNo,dec) )
                self.p300_draw.savePlotsD(self.p300.getArrTotalD(), self.pVal, 'dVal_%i_%i.png' %(self.epochNo,dec))

            self.send_func(pdf)
