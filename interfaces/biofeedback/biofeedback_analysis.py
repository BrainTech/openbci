#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import random
from obci.utils import context as ctx
import matplotlib.pyplot as plt

DEBUG = False

class BiofeedbackAnalysis(object):
    def __init__(self, send_func, sampling, 
                 context=ctx.get_dummy_context('BiofeedbackAnalysis')):
        self.logger = context['logger']
        self.send_func = send_func
        self.last_time = time.time()
        self.fs = sampling
        plt.ion()
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)

        
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
        self.logger.info("Got data to analyse... after: "+str(time.time()-self.last_time))
        self.logger.info("first and last value: "+str(data[0][0])+" - "+str(data[0][-1]))
        self.last_time = time.time()
        plt.clf()
        self.ax.plot(data[0])
        plt.draw()

        if random.random() > 0.5:
            self.send_func(1)
        else:
            self.logger.info("no decision")