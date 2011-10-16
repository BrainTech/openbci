#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sample_bci_analysis
import random, time
import analysis_logging as logger
LOGGER = logger.get_logger("sample_bci_analysis")

class SampleBCIAnalysis(object):
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
        return ['Freqs']

    def set_configs(self, configs):
        """Fired just after get_requested_configs is called and just before
        first call to .analyse()."""

        self.frequencies = [int(i) for i in configs['Freqs'].split(' ')]
        self.count = len(self.frequencies)

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
        
        LOGGER.info("Got data to analyse... after: "+str(time.time()-self.last_time))
        self.last_time = time.time()
        # here analyse data, and if you want make a decision like:
        dec = random.randint(0, self.count-1)
        # naturally if your dec value is of bad type, bad range 
        # (eg is bigger than self.count-1) then system`s behaviour is unexpected...
        # so be sure to define dec value properly

        # You should consider runnig some computation in a separate thread
        # as .analyse() is fired in the main thread, so by doing some slow stuff here
        # Your MX module can`t receive data online
        
        # lets send decision sometimes...
        if dec < self.count/2:
            self.send_func(dec)
