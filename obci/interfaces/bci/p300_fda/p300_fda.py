#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
P300 detectione based on Fisher's discriminant analysis

Author: Dawid Laszuk
Contact: laszukdawid@gmail.com
"""

import numpy as np
import scipy.stats as st
from signalAnalysis import DataAnalysis
from scipy.linalg import eig

import time, inspect

class P300_train:
    def __init__(self, channels, Fs, avrM, conN, csp_time=[0.2, 0.6], pPer=90):

        self.fs = Fs
        self.csp_time = np.array(csp_time)
        self.channels = channels

        self.defineConst(avrM, conN, pPer)
        self.defineMethods()
        
        
    def defineConst(self, avrM, conN, pPer):
        print "*"*5 + inspect.getframeinfo(inspect.currentframe())[2]
        
        # Define Const
        print "self.csp_time: ", self.csp_time
        self.tInit, self.tFin = self.csp_time
        self.iInit, self.iFin = np.floor( self.csp_time*self.fs)
        
        self.avrM = avrM  # Moving avr window length
        self.conN = conN  # No. of chan. to concatenate
        self.pPer = pPer # Nontarget percentile threshold

        # Target/Non-target arrays
        self.chL = len((self.channels).split(';'))
        self.arrL = self.avrM  # Length of data per channel

        # Data arrays
        totTarget = np.zeros( (self.chL, self.arrL))
        totNontarget = np.zeros((self.chL, self.arrL))

        # Flags
        self.classifiedFDA = -1 # 1 if classified with FDA
        
    def defineMethods(self):
        print "*"*5 + inspect.getframeinfo(inspect.currentframe())[2]

        # Declare methods
        self.sp = DataAnalysis(self.fs)
        self.sp.initConst(self.avrM, self.conN, self.csp_time)
        self.sp.set_lowPass_filter_ds(self.avrM/(self.csp_time[1]-self.csp_time[0]))
        #~ self.sp.set_highPass_filter(wp=2., ws=1., gpass=1., gstop=25.)

    def getTargetNontarget(self, signal, targetTags, nontargetTags):
        """
        Divides signal into 2 dicts: target & nontarget.
        """
        print "*"*5 + inspect.getframeinfo(inspect.currentframe())[2]
        
        # Reshapes data into trials x channels x data
        
        
        # Converts targets
        idxTarget = int(targetTags[0])
        target = signal[np.newaxis, :, idxTarget:idxTarget+self.fs]

        for tag in targetTags[1:]:
            index = int(tag)
            s = signal[np.newaxis, :, index:index+self.fs]
            target = np.concatenate( (target, s), axis=0)

        # Converts nontargets
        idxNontarget = int(nontargetTags[0])
        nontarget = signal[np.newaxis:, index:index+self.fs]
        
        for tag in ntrgTags[1:]:
            index = int(tag)
            s = signal[np.newaxis, :, index:index+self.fs]
            nontarget = np.concatenate( (nontarget, s), axis=0)
        
        return target, nontarget
    
    def prepareSignal(self, s):
        return self.sp.prepareSignal(s)

    def get_filter(self, c_max, c_min):
        print "*"*5 + inspect.getframeinfo(inspect.currentframe())[2]
        """This returns CSP filters

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
        vals, vects = eig(c_max, c_min)
        vals = vals.real
        vals_idx = np.argsort(vals)[::-1]
        P = np.zeros([len(vals), len(vals)])
        for i in xrange(len(vals)):
            #~ P[:,i] = vects[:,vals_idx[i]] / np.sqrt(vals[vals_idx[i]])
            P[:,i] = vects[:,vals_idx[i]]
        return P, vals[vals_idx]

    def train_csp(self, target, nontarget):
        print "*"*5 + inspect.getframeinfo(inspect.currentframe())[2]

        """Creates covariance matrices to be filtred with CSP.

            Parameters:
            -----------
            target : ndarray
                target signal matrix in shape TRIAL x CHANNELS x DATA.
            nontarget : ndarray
                not target signal matrix in shape TRIAL x CHANNELS x DATA.

            Returns:
            --------
            P : ndarray
                each column of this matrix is a CSP filter sorted in descending order
            vals : array-like
                corresponding eigenvalues
        """

        # Calcluate covariance matrices
        covTarget = np.zeros((self.chL,self.chL))
        covNontarget = np.zeros((self.chL,self.chL))

        # Lengths
        trgTrialsNo = target.shape[0]
        ntrgTrialsNo = nontarget.shape[0]

        # Target
        for idx in range(trgTrialsNo):
            A = np.matrix(target[idx])
            covTarget += np.cov(A)

        # NonTarget
        for idx in range(ntrgTrialsNo):
            A = np.matrix(nontarget[idx])
            covNontarget += np.cov(A)

        #~ totTarget = np.matrix(np.mean(target, axis=0))
        #~ totNtarget = np.matrix(np.mean(nontarget, axis=0))

        covTarget /= trgTrialsNo
        covNontarget /= ntrgTrialsNo

        return self.get_filter( covTarget, covNontarget+covTarget)
        

    def crossCheck(self, signal, target, nontarget):
        print "*"*5 + inspect.getframeinfo(inspect.currentframe())[2]
        """
        Cross validation over target and nontarget.
        """
        return self.valid_kGroups(signal, target, nontarget, 2)
    
    
    def valid_kGroups(self, signal, target, nontarget, K):
        print "*"*5 + inspect.getframeinfo(inspect.currentframe())[2]
        """
        Valid classifier.
        Divide signal into K groups then train classifier on K-1
        and test it on single groups.
        """

        # Determin CSP filter matrix
        self.P, vals = self.train_csp(target, nontarget)

        # Divide dicts into K groups
        target_kGroups = self.divideData(target, K)
        nontarget_kGroups = self.divideData(nontarget, K)

        # Determin shape of new matrices
        tShape = target_kGroups.shape
        train_tShape = ((tShape[0]-1)*tShape[1], tShape[2], tShape[3])
        
        ntShape = nontarget_kGroups.shape
        train_ntShape = ((ntShape[0]-1)*ntShape[1], ntShape[2], ntShape[3])
        
        # Buffers for dValues to determine their distributions
        dWholeTarget = np.zeros(tShape[0]*tShape[1])
        dWholeNontarget = np.zeros(ntShape[0]*ntShape[1])

        # For each group
        for i in range(K):
            
            # One group is test group
            target_test = target_kGroups[i]
            nontarget_test = nontarget_kGroups[i]
            
            # Rest of groups are training groups
            target_train = np.delete( target_kGroups, i, axis=0)
            target_train = target_train.reshape( train_tShape)

            nontarget_train = np.delete( nontarget_kGroups, i,axis=0)
            nontarget_train = nontarget_train.reshape( train_ntShape )
                
            # Determin LDA classifier values
            w, c = self.trainFDA(target_train, nontarget_train)
        
            # Test data
            dTarget, dNontarget = self.analyseData(target_test, nontarget_test, w, c)
            
            # Saves dValues
            dWholeTarget[i*len(dTarget):(i+1)*len(dTarget)] = dTarget
            dWholeNontarget[i*len(dNontarget):(i+1)*len(dNontarget)] = dNontarget
        
        
        self.saveDisributions( dWholeTarget, dWholeNontarget)
        
        meanDiff = self.compareDistributions(dWholeTarget, dWholeNontarget)
        
        return meanDiff
    
    def compareDistributions(self, target, nontarget):
        
        #~ # Calculates mean distance od dValues
        #~ meanDiff = np.mean(dWholeTarget) - np.mean(dWholeNontarget)
        
        #~ percentileList = [st.percentileofscore(nontarget, t) for t in target]
        #~ percentileSum = sum(percentileList)/len(target)
        #~ result = percentileSum 
        
        result = st.mannwhitneyu(nontarget, target)[0]
        
        return result
    
    def analyseData(self, target, nontarget, w, c):
        """
        Calculates dValues for whole given targets and nontargets.
        Perform by K-validation tests.
        """
        print "*"*5 + inspect.getframeinfo(inspect.currentframe())[2]
        

        # Test targets
        sTargetAnal = np.zeros((target.shape[0],w.shape[0]))
        sNontargetAnal = np.zeros((nontarget.shape[0],w.shape[0]))

        # 
        step = w.shape[0]/self.conN

        # Depending how many eigenvectors one want's to consider
        # from CSP,
        for idx in range(self.conN):
            # Dot product over all channels (CSP filter) and returns
            # array of (trials, data) shape.
            productTrg = np.dot( self.P[:,idx], target)
            productNtrg = np.dot( self.P[:,idx], nontarget)
            
            # Each data signal is analysed: filtred, downsized...
            analProductTrg = map( lambda sig: self.prepareSignal(sig), productTrg)
            analProductNtrg = map( lambda sig: self.prepareSignal(sig), productNtrg)
                        
            # Fills prepared buffer.
            sTargetAnal[:,idx*step:(idx+1)*step] = analProductTrg
            sNontargetAnal[:,idx*step:(idx+1)*step] = analProductNtrg

        # Calc dValues as: d = s*w - c
        dTarget = np.dot(sTargetAnal, w) - c
        dNontarget = np.dot(sNontargetAnal, w) - c

        return dTarget, dNontarget
        
    def divideData(self, D, K):
        """
        Separates given data dictionary into K subdictionaries.
        Used to perform K-validation tests.
        Takes:
          D -- numpy 3D matrix: EPOCH x CHANNEL x DATA
          K -- number of groups to divide to.
        Returns:
          kGroups -- numpy 4D matrix: GROUP_NO x EPOCH x CHANNEL x DATA
        """
        print "*"*5 + inspect.getframeinfo(inspect.currentframe())[2]
        
        L = D.shape[0]
        keys = np.arange(L)
        
        # Fill keys list with random trails utill it's diveable into K groups
        while( len(keys) % K != 0 ):
            keys = np.append( keys, np.random.randint(L))
        
        # Shuffle list
        np.random.shuffle(keys)
        
        # Divide given matrix into K_groups
        step = len(keys)/K
        kGroups = np.empty( (K,step,D.shape[1], D.shape[2]))
        for idx in range(K):
            kGroups[idx] = D[keys[idx*step:(idx+1)*step]]

        return kGroups
        
    def trainClassifier(self, signal, trgTags, ntrgTags):
        print "*"*5 + inspect.getframeinfo(inspect.currentframe())[2]
        target, nontarget = self.getTargetNontarget(signal, trgTags, ntrgTags)
        self.P, vals = self.train_csp(target, nontarget)
        
        self.trainFDA(target, nontarget)
        
    def trainFDA(self, target, nontarget):
        print "*"*5 + inspect.getframeinfo(inspect.currentframe())[2]
        
        #~ target = np.matrix(target)
        #~ nontarget = np.matrix(nontarget)
        
        goodAnal = np.empty((target.shape[0],self.conN*self.avrM))
        badAnal = np.empty((nontarget.shape[0],self.conN*self.avrM))
        
        for con in range(self.conN):
            productCSPTrg = np.dot( self.P[:,con], target)
            productCSPNtrg = np.dot( self.P[:,con], nontarget)
            
            # Each data signal is analysed: filtred, downsized...
            analProductCSPTrg = np.array(map( lambda sig: self.prepareSignal(sig), productCSPTrg))
            analProductCSPNtrg = np.array(map( lambda sig: self.prepareSignal(sig), productCSPNtrg))

            goodAnal[:,con*self.avrM:(con+1)*self.avrM] = analProductCSPTrg
            badAnal[:,con*self.avrM:(con+1)*self.avrM] = analProductCSPNtrg

        ### TARGET
        gAnalMean = goodAnal.mean(axis=0)
        gAnalCov = np.cov(goodAnal, rowvar=0)

        bAnalMean = badAnal.mean(axis=0)
        bAnalCov = np.cov(badAnal, rowvar=0)
        
        # Mean diff
        meanAnalDiff = gAnalMean - bAnalMean
        #~ meanAnalMean = 0.5*(gAnalMean + bAnalMean)

        A = gAnalCov + bAnalCov
        invertCovariance = np.linalg.inv( A )

        # w - normal vector to separeting hyperplane
        # c - treshold for data projection
        self.w = np.dot( invertCovariance, meanAnalDiff)
        self.c = st.scoreatpercentile(np.dot(self.w, badAnal.T), self.pPer)
        #~ self.c = np.dot(self.w, meanAnalMean)

        
        #~ print "We've done a research and it turned out that best values for you are: "
        #~ print "w: ", self.w
        #~ print "c: ", self.c
        #~ print "w.shape: ", self.w.shape
        np.save('w',self.w)
        np.save('c',self.c)
        
        return self.w, self.c
    
    def isClassifiedFDA(self):
        """
        Returns True, if data has already been classified.
        """
        print "*"*5 + inspect.getframeinfo(inspect.currentframe())[2]
        return self.classifiedFDA
        
    def getPWC(self):
        """
        If classifier was taught, returns CSP Matrix as [P],
        classifier seperation vector [w] and classifier separation value [c].
        Else returns -1.
        """
        print "*"*5 + inspect.getframeinfo(inspect.currentframe())[2]
        if self.classifiedFDA:
            return (self.P, self.w, self.c)
        else:
            return -1
        
    def saveDisributions(self, dTarget, dNontarget):
        self.dTarget = dTarget
        self.dNontarget = dNontarget
    
    def getDValDistribution(self):
        return self.dTarget, self.dNontarget

    def saveDist2File(self, targetName, nontargetName):
        np.save(targetName, self.dTarget)
        np.save(nontargetName, self.dNontarget)
            
class P300_analysis(object):
    def __init__(self, sampling, cfg={}, fields=8):
        
        self.fs = sampling
        self.fields = fields
        
        self.defineConst(cfg)
        self.defineMethods()
        
    def defineConst(self, cfg):

        # moving avr & resample factor
        self.avrM = int(cfg['avrM'])
        
        # Concatenate number of CSP vectors
        self.conN = int(cfg['conN'])  

        # Define analysis time
        self.csp_time = np.array(cfg['csp_time'])
        self.tInit, self.tFin = self.csp_time
        self.iInit, self.iFin = np.floor(self.csp_time*self.fs)

        self.chL = len(cfg['use_channels'].split(';'))
        self.arrL = self.avrM

        self.nLast = int(cfg['nLast'])
        self.nMin = int(cfg['nMin'])
        self.nMax = int(cfg['nMax'])
        
        self.dec = -1

        # Arrays
        self.flashCount = np.zeros(self.fields)  # Array4 flash counting
        self.dArr = np.zeros(self.fields) # Array4 d val
        
        self.dArrTotal = {}
        for i in range(self.fields): self.dArrTotal[i] = np.array([])
        
        self.sAnalArr = {}
        for i in range(self.fields): self.sAnalArr[i] = np.zeros( self.arrL*self.conN)
        
        # For statistical analysis
        self.per = np.zeros(self.fields)
        self.pPer = float(cfg['pPercent'])
        self.pdf = np.array(cfg['pdf'])

    def newEpoch(self):
        self.flashCount = np.zeros(self.fields)  # Array4 flash counting
        self.dArr = np.zeros(self.fields) # Array4 d val

        for i in range(self.fields): self.dArrTotal[i] = np.array([])

    
    def defineMethods(self):
        # Declare methods
        self.sp = DataAnalysis(self.fs)
        self.sp.initConst(self.avrM, self.conN, self.csp_time)
        #~ self.sp.set_lowPass_filter_ds(self.avrM/(self.csp_time[1]-self.csp_time[0]))
        
    def prepareSignal(self, signal):
        return self.sp.prepareSignal(signal)
        
    def testData(self, signal, blink):

        # Analyze signal when data for that flash is neede
        s = np.empty( self.avrM*self.conN)
        for con in range(self.conN):
            s[con*self.avrM:(con+1)*self.avrM] = self.prepareSignal(np.dot(self.P[:,con], signal))
        
        # Data projection on Fisher's space
        self.d = np.dot(s,self.w) - self.c
        self.dArr[blink] += self.d
        self.dArrTotal[blink] = np.append(self.d, self.dArrTotal[blink])
        self.dArrTotal[blink] = self.dArrTotal[blink][:self.nMax]
        
        self.flashCount[blink] += 1
        
        #~ print "self.d: ", self.d
        
    def isItEnought(self):
        #print "self.flashCount: ", self.flashCount
        if (self.flashCount <= self.nMin).any():
            return -1
        elif (self.flashCount >= self.nMax).all():
            self.forceDecision()
        else:
            return self.testSignificances()
        
    def testSignificances(self):
        """
        Test significances of d values.
        If one differs MUCH number of it is returned as a P300 target.
        
        Temporarly, as a test, normal distribution boundries for pVal
        percentyl are calulated. If only one d is larger than that pVal
        then that's the target.
        """
        #print "++ testSignificances ++ "
        
        dMean = np.zeros(self.fields)
        
        for i in range(self.fields):
            dMean[i] = self.dArrTotal[i][:self.nLast].mean()
        
        self.per = [st.percentileofscore(self.pdf, x) for x in dMean]
        self.per = np.array(self.per)
        
        #~ print "dMean: ", dMean
        #print "percentile: ", self.per

        # If only one value is significantly distant
        if np.sum(self.per > self.pPer) == 1:
            self.dec = np.arange(self.fields)[self.per==self.per.max()]
            self.dec = np.int(self.dec[0])
            print "wybrano -- {0}".format(self.dec)

            return self.dec
        
        else:
            return -1

    def forceDecision(self):
        #print " ++ forceDecision ++ "
        
        self.testSignificances()

        # If only one value is significantly distant 
        # Decision is the field with largest w value
        self.dec = np.arange(self.per.shape[0])[self.per==np.max(self.per)]
        self.dec = np.int(self.dec[0])

        # Return int value
        return self.dec
        
    def setPWC(self, P, w, c):
        self.P = P
        self.w = w
        self.c = c

    def setPdf(self, pdf):
        self.pdf = pdf

    def getDecision(self):
        return self.dec

    def getArrTotalD(self):
        return self.dArrTotal

    def getRecentD(self):
        return self.d
        
    def getArrD(self):
        return self.dArr
    
    def getProbabiltyDensity(self):
        """
        Returns percentiles of given scores
        from nontarget propabilty density function.
        """
        
        dMean = np.zeros(self.fields)
        nMin = self.flashCount.min()
        #~ print "nMin: ", nMin
        for i in range(self.fields):
            dMean[i] = self.dArrTotal[i][:nMin].mean()

        # Assuming that dValues are from T distribution
        p = map( lambda score: st.percentileofscore(self.pdf, score), dMean)
        
        return p
        
