#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import numpy, cPickle, os, time, sys, random, variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client
#import mrygacz

import ugm_logging as logger
LOGGER = logger.get_logger("ugm_feedback_server")

class UgmFeedbackServer(object):
    def __init__(self):
        
        self.ugm_update_message = [
            {'id':30000,
             'feedback_level':0},
            {'id':30001,
             'feedback_level':0},
            {'id':30002,
             'feedback_level':0},
            {'id':30003,
             'feedback_level':0},
            {'id':30004,
             'feedback_level':0},
            {'id':30005,
             'feedback_level':0},
            {'id':30006,
             'feedback_level':0},
            {'id':30007,
             'feedback_level':0}]

        self.connection = connect_client(type = peers.ANALYSIS)
        
        self.numOfFreq = int(self.connection.query(message = "NumOfFreq", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)		
        
        self.border = float( self.connection.query(message = "Border", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.repeats = float( self.connection.query(message = "Repeats", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)

        self.sampling_rate = int(self.connection.query(message="SamplingRate", type=types.DICT_GET_REQUEST_MESSAGE).message)
       
        self.indexMap = self.numOfFreq * [0]

        # allFreqs - list of all frequencies  
        allFreqs = self.connection.query(message="Freqs", type=types.DICT_GET_REQUEST_MESSAGE).message
        allFreqs = allFreqs.split(" ")
        for i in range(len(allFreqs)):
            allFreqs[i] = int(allFreqs[i])
         
               
        # list of non-zero frequencies and their harmonics - the frequencies which will be used in analysis
        self.freqs = (self.numOfFreq * 3) * [0]
        j = 0
        for i in range(self.numOfFreq):
            while (allFreqs[j] == 0):
                j += 1
            self.freqs[i] = allFreqs[j]
            self.indexMap[i] = j
            self.freqs[i + self.numOfFreq] = 2 * allFreqs[j]
            self.freqs[i + (2 * self.numOfFreq)] = 3 * allFreqs[j]
            j += 1

        self.lastChoice = -2 # contains index of lastly chosen frequency
        self.repCounter = 0 # how many times the choice repeated

    def run(self):
        while True:
            self.analyse()

    def analyse(self):

        numOfFreq = self.numOfFreq
        data = variables_pb2.SampleVector()
        #data = self.connection.query(message = str(0), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message
        data.ParseFromString(self.connection.query(message = str(0), type = types.SIGNAL_CATCHER_REQUEST_MESSAGE, timeout = 10).message)
        #d = cPickle.loads(data)
        d = []
        for s in data.samples:
            d.append(s.value)
# TODO: cos tu nie gralo, na poczatku czasem przychodzilo mniej danych i sypalo sie
#        if len(d) < 500:
#            print("ZEEERO")
#            print(len(d))
#            return 
#        else:
#            pass
#            print("NIE:")
#            print(len(d))
        #d = list(d)
        #rint "d: ", d
        mul = 4
        d = d[-int(self.sampling_rate * mul):]
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
        mx = float(max(diffs))
        for i, msg_dict in enumerate(self.ugm_update_message):
            msg_dict['feedback_level'] = abs(diffs[int(msg_dict['id'])-30000]/mx) #FIXME
        l_msg = variables_pb2.UgmUpdate()
        l_msg.type = 1
        l_msg.value = str(self.ugm_update_message)
        #LOGGER.info("Prepare sending: "+ l_msg.value)
        self.connection.send_message(
            message = l_msg.SerializeToString(), 
            type=types.UGM_UPDATE_MESSAGE, flush=True)

if __name__ == "__main__":
    UgmFeedbackServer().run()

