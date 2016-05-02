#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import time
import random
from obci.utils import context as ctx
import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import rfft,fft,fftfreq,fftshift


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
        self.ax = self.fig.gca()
        self.i = 0
        #self.config= config

#    def _calculate_fft(self, dane, fs):
#        return analiza.calculat_fft(.....)
    def widmo_mocy(self, s):
            S = fft(s)/np.sqrt(len(s))
            S_moc = S*S.conj()
            S_moc = S_moc.real
            F = fftfreq(len(s), 1/self.fs)
            return (fftshift(F),fftshift(S_moc))
            
    def energia_w_pasmie(self, moc_0, moc_1):
        #8-13
        os_x = moc_0
        start = np.where(os_x==8.)[0][0] #528
        stop = np.where(os_x==13.)[0][0] #538
        wynik_energia = 0
        
        for i in xrange(int(start), int(stop)+1,1):
            wynik_energia += moc_1[i]**2
            
        punkt_zero = np.where(os_x==0.)[0][0]  #512
        wynik0= moc_1[punkt_zero]**2+ moc_1[punkt_zero+1]**2 + moc_1[punkt_zero+2]**2
        
        #self.logger.info("wartosc mocy: "+str(wynik0>wynik_energia)) #sprawdzenie czy moc w zerze jest wieksza od mocy w pasmie
        return start, stop, wynik_energia/float(stop-start), wynik0/3.
        
    def analyse(self, data):
        self.logger.info("*********************")
        self.logger.info("data.shape:{}".format(data.shape))
        """
        Fired as often as defined in hashtable configuration:
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
      #  data_filtered = self._filter_butter_data(data, 1.,'highpass' )
    #data_filtered = self._filter_butter_data(data)
    #data_filtered = self._filter_butter_data(data)
        
        plt.cla()
        self.logger.info("Got data to analyse... after: "+str(time.time()-self.last_time))
        self.logger.info("first and last value: "+str(data[0][0])+" - "+str(data[0][-1]))
        

        self.last_time = time.time()
        
            
        policzona_moc=self.widmo_mocy(data[0])
        
        self.ax.plot(policzona_moc[0],policzona_moc[1] )
        self.ax.set_xlim(0,self.fs/2)
        plt.draw()
        
        start, stop, energia_w_pasmie, wynik0 = self.energia_w_pasmie(policzona_moc[0],policzona_moc[1])
        self.logger.info('energia w pasmie'+str(energia_w_pasmie)+' energia  w okolicach 0'+str(wynik0))


        if random.random() > 0.5:
            self.send_func(1)
        else:
            self.logger.info("no decision")
            
