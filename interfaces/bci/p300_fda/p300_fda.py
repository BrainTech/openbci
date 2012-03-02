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
    def __init__(self, channels, Fs, avrM, conN, csp_time=[0.2, 0.6]):

        
        self.Fs = Fs
        self.t = np.array(csp_time)
        self.channels = channels

        self.defineConst(avrM, conN)
        self.defineMethods()
        
        
    def defineConst(self, avrM, conN):
        
        # Define Const
        self.tInit, self.tFin = self.t
        self.iInit, self.iFin = np.floor( self.t*self.Fs)
        
        self.avrM = avrM  # Moving avr window length
        self.conN = conN  # No. of chan. to concatenate

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

        for tag in trgTags:

            index = int(tag)
            s = np.zeros( (self.chL, self.arrL) )
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

        print "channels: ", self.channels
        print "trgTags[0]: ", trgTags[0]
        print "target.shape: ", len(target)
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
        self.avrM = cfg['avrM']  # VAR !
        
        # Concatenate No. of signals
        self.conN = cfg['conN']  # VAR !

        # Define analysis time
        self.t = np.array(cfg['csp_time'])
        self.tInit, self.tFin = self.t
        self.iInit, self.iFin = np.floor(self.t*self.Fs)

        self.chL = len(cfg['use_channels'])
        self.arrL = np.floor((self.iFin-self.iInit)/self.avrM)

        self.nRepeat = cfg['nRepeat']
        self.nMin = 3
        self.dec = -1

        #
        self.dArr = np.zeros(self.fields) # Array4 d val
        #~ self.dArrTotal = np.zeros((10,self.fields)) # Array4 d val
        self.dArrTotal = {}
        for i in range(self.fields): self.dArrTotal[i] = np.array([])
        
        self.flashCount = np.zeros(self.fields)  # Array4 flash counting
        self.sAnalArr = {}
        for i in range(self.fields): self.sAnalArr[i] = np.zeros( self.arrL*self.conN)
        
        # For statistical analysis
        p = cfg['pVal']
        self.z = st.norm.ppf(p)
    
    def defineMethods(self):
        self.filtr = Filtr(self.Fs)

    def prepareSignal(self, signal):
        s = np.zeros((self.chL, self.arrL))
        for ch in xrange(self.chL):
            temp = signal[ch]
            temp = self.filtr.filtrHigh(temp)
            temp = self.filtr.filtrLow(temp)
            temp = (temp - temp.mean())/temp.std()
            temp = temp[self.iInit:self.iFin:self.avrM]
            
            s[ch] = temp
        
        sAnal = np.array( [] )
        for idx in range(self.conN):
            sAnal = np.concatenate( (sAnal, np.dot( self.P[:, idx], s)) )

        return sAnal
        
    def testData(self, signal, blink):

        # Analyze signal when data for that flash is neede
        s = self.prepareSignal(signal)
        
        # Data projection on Fisher's space
        self.d = np.dot(s,self.w) - self.c
        self.dArr[blink] += self.d
        self.dArrTotal[blink] = np.append(self.dArrTotal[blink], self.d)
        
        self.flashCount[blink] += 1
        
        #~ print "self.d: ", self.d
        
    def isItEnought(self):
        if (self.flashCount < self.nMin).any():
            return -1

        return self.testSignificances()
        
    def testSignificances(self):
        """
        Test significances of d values.
        If one differs MUCH number of it is returned as a P300 target.
        
        Temporarly, as a test, normal distribution boundries for pVal
        percentyl are calulated. If only one d is larger than that pVal
        then that's the target.
        """
        
        dMean = np.zeros(self.fields)
        nMin = self.flashCount.min()
        print "nMin: ", nMin
        for i in range(self.fields):
            dMean[i] = self.dArrTotal[i][:nMin].mean()
        
        print "nMin = ", nMin
        print "dMean: ", dMean
        
        #~ dMean = self.dArr / self.flashCount
        w = np.zeros(self.fields)
        for sq in range(self.fields):
            # Norm distribution
            tmp = np.delete(dMean, sq)
            mean, std = tmp.mean(), tmp.std()
            
            # Find right boundry
            v = mean + self.z*std

            # Calculate distance
            w[sq] = dMean[sq]-v
            
            print "{0}: (m, std, v) = ({1}, {2}, {3})".format(sq, mean, std, v)
            print "{0}: (d, w) = ({1}, {2})".format(sq, dMean[sq], w[sq])
            

        # If only one value is significantly distant
        if np.sum(w>0) == 1:
            #~ return True
            self.dec = np.arange(8)[w>0]
            print "wybrano -- {0}".format(self.dec)

            return int(self.dec[0])
        
        return -1

    def forceDecision(self):

        w = np.zeros(self.fields)
        for sq in range(self.fields):
            # Norm distribution
            tmp = np.delete(self.dArr, sq)
            mean, std = tmp.mean(), tmp.std()
            
            # Find right boundry
            v = mean + self.z*std
            
            # Calculate distance
            w[sq] = self.dArr[sq]-v

            print "{0}: (m, std, v) = ({1}, {2}, {3})".format(sq, mean, std, v)
            print "     (d, w)      = ({1}, {2})".format(sq, self.dArr[sq], w[sq])   

        # If only one value is significantly distant 
        self.dec = np.arange(w.shape[0])[w==np.max(w)]
        print "self.dec: ", self.dec

        return self.dec
        
    def setPWC(self, P, w, c):
        self.P = P
        self.w = w
        self.c = c

    def getDecision(self):
        return self.dec

    def newEpoch(self):
        self.flashCount = np.zeros(self.fields)  # Array4 flash counting

        for i in range(self.fields): self.dArrTotal[i] = np.array([])
        self.dArr = np.zeros(w.shape[0]) # Array4 d val

         # Array4 d val
    
    def getArrTotalD(self):
        return self.dArrTotal

    def getRecentD(self):
        return self.d
        
    def getArrD(self):
        return self.dArr
