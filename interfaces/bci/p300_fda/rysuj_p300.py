#!/usr/bin/python
# coding: UTF-8
import numpy as np
import pylab as py  

import scipy.io
import scipy.stats as st
import signalParser as sp
from Filtr import Filtr
import sys, os, time


#~ filtr = Filtr(Fs)

class P300_draw(object):
    def __init__(self, target, nontarget, trgTags, ntrgTags, fs=128):

        # Sorting tags... (for no real reason)
        trgTags.sort()
        ntrgTags.sort()
        
        #~ print "target: ", target
        #~ print "nontarget: ", nontarget
        
        # Setting arrays/dicts
        self.target = target 
        self.nontarget = nontarget
        self.trgTags = trgTags
        self.ntrgTags = ntrgTags
        
        self.fs = fs
        
    def setTimeLine(self, conN, avrM, csp_time=[0,1]):
        tMin, tMax = csp_time[0], csp_time[1]
        self.conN = conN
        self.avrM = avrM
        self.simpleT = np.arange(tMin, tMax, (1.*avrM)/self.fs)
        self.CSP_t = np.arange(tMin, tMax + (tMax-tMin)*(self.conN-1), (self.avrM*1.)/self.fs)
        
    def setCSP(self, P):
        self.P = P
        
    def plot(self):
        
        tmp = self.target[self.trgTags[0]]
        if self.P==None:
            self.P = np.ones(tmp.shape)
        
        print "tmp: ", tmp
        print "self.P: ", self.P
        P = self.P
        # Plots
        py.figure()

        L = tmp.mean(axis=0).shape[0]
        meanMeanSimpleTarget = np.zeros( L )
        meanMeanCSPTarget = np.zeros( self.conN*L )
        
        meanMeanSimpleNontarget = np.zeros( L )
        meanMeanCSPNontarget = np.zeros( self.conN*L )

        print "meanMeanSimpleTarget.shape: ", meanMeanSimpleTarget.shape
        print "meanMeanCSPTarget.shape: ",meanMeanCSPTarget.shape
        print "meanMeanSimpleNontarget.shape: ", meanMeanSimpleNontarget.shape
        print "meanMeanCSPNontarget.shape: ", meanMeanCSPNontarget.shape
        
        print "self.trgTags: ", self.trgTags 
        
        
        ## Plotting target ##
        for idx, tag in enumerate(self.trgTags):
            
            s = self.target[tag]
            meanCSPTarget = np.array([])
            for n in range(self.conN):
                meanCSPTarget = np.concatenate((meanCSPTarget, np.dot( P[:,n], s)) )
            meanMeanCSPTarget += meanCSPTarget

            meanSimpleTarget = s.mean(axis=0)
            meanMeanSimpleTarget += meanSimpleTarget

            
            py.subplot(2,2,1)

            py.plot(self.simpleT, meanSimpleTarget,'g-')
            #~ py.plot(meanSimpleTarget,'g-')

            print "self.CSP_t.shape: ", self.CSP_t.shape
            print "meanCSPTarget.shape: ", meanCSPTarget.shape
            py.subplot(2,2,2)
            py.plot(self.CSP_t, meanCSPTarget, 'g-')
            #~ py.plot(meanCSPTarget, 'g-')

        py.subplot(2,2,1)
        py.title("Simple mean target")
        py.plot(self.simpleT, meanMeanSimpleTarget/len(self.trgTags), 'r-')
        #~ py.plot(meanMeanSimpleTarget, 'r-')
        
        py.subplot(2,2,2)
        py.title("CSP mean target")
        #~ py.plot(t, meanMeanCSPTarget, 'r-')
        py.plot(self.CSP_t, meanMeanCSPTarget/len(self.trgTags), 'r-')
        #~ py.plot( meanMeanCSPTarget, 'r-')
        
        ## Plotting non target ##
        for idx, tag in enumerate(self.ntrgTags):
            
            s = self.nontarget[tag]
            meanCSPNontarget = np.array([])
            for n in range(self.conN):
                meanCSPNontarget = np.concatenate((meanCSPNontarget, np.dot( P[:,n], s)) )
            meanMeanCSPNontarget += meanCSPNontarget

            meanSimpleNontarget = s.mean(axis=0)
            meanMeanSimpleNontarget += meanSimpleNontarget

            
            py.subplot(2,2,3)
            py.plot(self.simpleT, meanSimpleNontarget,'g-')
            #~ py.plot( meanSimpleNontarget,'g-')

            py.subplot(2,2,4)
            py.plot(self.CSP_t, meanCSPNontarget, 'g-')
            #~ py.plot( meanCSPNontarget, 'p-')

        py.subplot(2,2,3)
        py.title("Simple mean nontarget")
        py.plot(self.simpleT, meanMeanSimpleNontarget/len(self.ntrgTags), 'r-')
        #~ py.plot(meanMeanSimpleNontarget, 'r-')

        py.subplot(2,2,4)
        py.title("CSP mean target")
        py.plot(self.CSP_t, meanMeanCSPNontarget/len(self.ntrgTags), 'r-')
        #~ py.plot(meanMeanCSPNontarget, 'r-')

        py.show()
    
