#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
P300 detectione based on Fisher's discriminant analysis

Author: Dawid Laszuk
Contact: laszukdawid@gmail.com
"""

import numpy as np
import scipy.stats as st
from Filtr import Filtr
from scipy.linalg import eig


class P300_train:
    def __init__(self, channels, Fs, csp_time=[0.2, 0.6]):

        
        self.Fs = Fs
        self.t = np.array(csp_time)
        self.channels = channels
        
        self.defineConst()
        self.defineMethods()
        
        
    def defineConst(self):
        
        #~ self.Fs = 128. # Hz
        
        # Define Const
        self.tInit, self.tFin = self.t
        self.iInit, self.iFin = np.floor( self.t*self.Fs)
        
        self.avrM = 4  # Moving avr window length
        self.conN = 7  # No. of chan. to concatenate

        # Target/Non-target arrays
        self.chL = len(self.channels)
        self.arrL = (self.iFin-self.iInit)/self.avrM  # Length of data per channel

        # Data arrays
        totTarget = np.zeros( (self.chL, self.arrL))
        totNontarget = np.zeros((self.chL, self.arrL))

        self.good = np.zeros(self.arrL*self.conN)
        self.bad  = np.zeros(self.arrL*self.conN)
        good_count, bad_count = 0, 0
        
        # Flags
        self.classifiedFDA = -1 # 1 if classified with FDA
        
    def defineMethods(self):
        # Declare methods
        self.filtr = Filtr(self.Fs)

    def getTargetNontarget(self, signal, targetTags, nontargetTags):
        target = {}
        trgTags = targetTags
        print "*"*10
        print "trgTags: ", trgTags
        print "*"*10
        
        for tag in trgTags:
            index = int(tag)
            s = np.zeros( (self.chL, self.arrL) )
            print "signal[0].shape: ", signal[0]
            for idx in range(self.chL):
                temp = signal[idx][index:index+self.Fs]
                temp = (temp-temp.mean())/temp.std()
                temp = temp[self.iInit:self.iFin:self.avrM]
                s[idx] = temp
            
            target[tag] = s

        nontarget = {}
        ntrgTags = nontargetTags
        for tag in ntrgTags:
            index = int(tag)
            s = np.zeros( (self.chL, self.arrL) )
            for idx in range(self.chL):
                temp = signal[idx][index:index+self.Fs]
                temp = (temp-temp.mean())/temp.std()
                temp = temp[self.iInit:self.iFin:self.avrM]
                s[idx] = temp
            
            nontarget[tag] = s
        
        return target, nontarget

    def get_filter(self, c_max, c_min):
        """This retzurns CSP filters

            Function returns array. Each column is a filter sorted in descending order i.e. first column represents filter that explains most energy, second - second most, etc.

            Parameters:
            -----------
            c_max : ndarray
                covariance matrix of signal to maximalize.
            c_min : ndarray
                covariance matrix of signal to minimalize.

            Returns:
            --------
            P : ndarray
                each column of this matrix is a CSP filter sorted in descending order
            vals : array-like
                corresponding eigenvalues
        """
        vals, vects = eig(c_max, c_min + c_max)
        vals = vals.real
        vals_idx = np.argsort(vals)[::-1]
        P = np.zeros([len(vals), len(vals)])
        for i in xrange(len(vals)):
            P[:,i] = vects[:,vals_idx[i]] / np.sqrt(vals[vals_idx[i]])
        return P, vals[vals_idx]

    def train_csp(self, target, nontarget, trgTags, ntrgTags):
        print "len(trgTags): ", len(trgTags)
        covTarget = np.zeros( (self.chL,self.chL) )
        covNontarget = np.zeros( (self.chL,self.chL) )
        
        print "target[tag].shape: ", target[trgTags[0]].shape
        # Target
        for tag in trgTags:
            s = target[tag]
            A = np.matrix(s)

            cov = A*A.T
            cov /= np.trace(cov)
            covTarget  += cov

        # NonTarget
        for tag in ntrgTags:
            s = nontarget[tag]
            A = np.matrix(s)

            cov = A*A.T
            cov /= np.trace(cov)
            covNontarget += cov
                
        covTarget /= trgTags.shape[0]
        covNontarget /= ntrgTags.shape[0]

        return self.get_filter( covTarget, covTarget + covNontarget)


    def trainClassifier(self, signal, trgTags, ntrgTags):

        target, nontarget = self.getTargetNontarget(signal, trgTags, ntrgTags)
        P, vals = self.train_csp(target, nontarget, trgTags, ntrgTags)
        self.P = P
        
        # Target
        for tag in trgTags:
            s = target[tag]

            sig = np.array([])
            for idx in range(self.conN):
                sig = np.concatenate( (sig, np.dot(P[:,idx],s)))

            self.good = np.vstack( (self.good, sig))

        # Non-target
        for tag in ntrgTags:
            s = nontarget[tag]

            sig = np.array([])
            for idx in range(self.conN):
                sig = np.concatenate( (sig, np.dot(P[:,idx],s)))

            self.bad = np.vstack( (self.bad,sig))
                
        ### GOOD
        print "good_count = ", trgTags.shape[0]
        self.good = self.good[1:]
        gMean = self.good.mean(axis=0)
        gCov = np.cov(self.good, rowvar=0)
        
        goodAnal = self.good
        gAnalMean = goodAnal.mean(axis=0)
        gAnalCov = np.cov(goodAnal, rowvar=0)

        ### BAD
        print "bad_count = ", ntrgTags.shape[0]
        self.bad = self.bad[1:]
        bMean = self.bad.mean(axis=0)
        bCov = np.cov(self.bad, rowvar=0)

        badAnal = self.bad
        bAnalMean = badAnal.mean(axis=0)
        bAnalCov = np.cov(badAnal, rowvar=0)
        
        # Mean diff
        meanAnalDiff = gAnalMean - bAnalMean
        meanAnalMean = 0.5*(gAnalMean + bAnalMean)

        A = gAnalCov + bAnalCov
        invertCovariance = np.linalg.inv( gAnalCov + bAnalCov )

        # w - normal vector to separeting hyperplane
        # c - treshold for data projection
        self.w = np.dot( invertCovariance, meanAnalDiff)
        self.c = np.dot(self.w, meanAnalMean)

        #~ print "We've done a research and it turned out that best values for you are: "
        #~ print "w: ", self.w
        #~ print "c: ", self.c
        #~ print "w.shape: ", self.w.shape
        np.save('w',self.w)
        np.save('c',self.c)
    
    def isClassifiedFDA(self):
        return self.classifiedFDA
        
    def getPWC(self):
        if self.classifiedFDA:
            return (self.P, self.w, self.c)
        else:
            return -1
    
            
class P300_analysis(object):
    def __init__(self, sampling, cfg={}, fields=8):
        
        self.Fs = sampling
        self.fields = fields
        
        self.defineConst(cfg)
        self.defineMethods()
        
    def defineConst(self, cfg):

        # moving avr & resample factor
        self.avrM = 4  # VAR !
        
        # Concatenate No. of signals
        self.conN = 7  # VAR !

        # Define analysis time
        self.t = np.array(cfg['csp_time'])
        self.tInit, self.tFin = self.t
        self.iInit, self.iFin = np.floor(self.t*self.Fs)

        self.chL = len(cfg['use_channels'].split(';'))
        self.arrL = np.floor((self.iFin-self.iInit)/self.avrM)

        #
        self.dArr = np.zeros(self.fields) # Array4 d val
        self.flashCount = np.zeros(self.fields)  # Array4 flash counting
        self.sAnalArr = {}
        for i in range(self.fields): self.sAnalArr[i] = np.zeros( self.arrL*self.conN)
        
        # For statistical analysis
        p = cfg['pVal']
        self.z = st.norm.ppf(p)
    
    def defineMethods(self):
        self.filtr = Filtr(self.Fs)

    def prepareSignal(self, signal):
        
        print "*"*40

        
        s = np.zeros((self.chL, self.arrL))
        for ch in xrange(self.chL):
            print "ch: ", ch
            temp = signal[ch]
            temp = self.filtr.filtrHigh(temp)
            temp = self.filtr.filtrLow(temp)
            temp = (temp - temp.mean())/temp.std()
            temp = temp[self.iInit:self.iFin:self.avrM]
            
            print "temp: ", temp
            print "temp.shape: ", temp.shape
            print "self.arrL: ", self.arrL
            print "s[ch]: ", s[ch].shape
            s[ch] = temp
        
        sAnal = np.array( [] )
        for idx in range(self.conN):
            sAnal = np.concatenate( (sAnal, np.dot( self.P[:, idx], s)) )

        print "*"*40
        print "\n"*4

        
        return sAnal
        
    def testData(self, signal, blink):
        s = self.prepareSignal(signal)

        self.d = np.dot(s,self.w) - self.c
        self.dArr[blink] += self.d
        
        return self.testIfEnd()
        
    def getRecentD(self):
        return self.d
        
    def getArrD(self):
        return self.dArr
        
    def testIfEnd(self):
        """
        Test significances of d values.
        If one differs MUCH number of it is returned as a P300 target.
        
        Temporarly, as a test, normal distribution boundries for pVal
        percentyl are calulated. If only one d is larger than that pVal
        then that's the target.
        """
        
        dNorm = np.zeros(8)
        w = np.zeros(8)
        for sq in range(8):
            # Norm distribution
            tmp = np.delete(self.dArr, sq)
            mean, std = tmp.mean(), tmp.std()
            dNorm[sq] = (self.dArr[sq]-mean)/std
            
            # Find right boundry
            v = mean+self.z*std
            
            # Calculate distance
            w[sq] = self.dArr[sq]-v
        
        print "w: ", w
        # If only one value is significantly distant
        if np.sum(w>0) == 1:
            self.dec = np.arange(8)[w>0]
            print "wybrano -- {0}".format(self.dec)
            self.dArr = np.zeros(8) # Array4 d val
            return int(self.dec[0])
        
        return -1
        
    def setPWC(self, P, w, c):
        self.P = P
        self.w = w
        self.c = c

    def getDecision(self):
        return self.dec
