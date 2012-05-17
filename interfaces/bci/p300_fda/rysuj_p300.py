#!/usr/bin/python
# coding: UTF-8
import numpy as np
import pylab as py  

import scipy.io
import scipy.stats as st
from signalAnalysis import DataAnalysis
import sys, os, time


#~ filtr = Filtr(Fs)

class P300_draw(object):
    def __init__(self, target, nontarget, trgTags, ntrgTags, fs=128.):

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
        self.defineMethods()
        
    def setTimeLine(self, conN, avrM, csp_time=[0,1]):
        
        self.csp_time = csp_time
        tMin, tMax = csp_time[0], csp_time[1]
        self.conN = conN
        self.avrM = avrM

        self.simpleT = np.arange(tMin, tMax, self.avrM*1./self.fs)
        self.CSP_t = np.arange(tMin, tMax + (tMax-tMin)*(self.conN-1), self.avrM*1./self.fs)

        self.iInit = int(tMin*self.fs)
        self.iFin = int(tMax*self.fs)
        
        self.sp.initConst(avrM, conN, csp_time)
        
    def setCSP(self, P):
        self.P = P

    def defineMethods(self):
        self.sp = DataAnalysis(self.fs)
        

    def prepareSignal(self, s):
        return self.sp.prepareSignal(s)
        
    def plot(self):
        
        tmp = self.target[self.trgTags[0]]
        if self.P==None:
            self.P = np.ones(tmp.shape)
        
        P = self.P
        # Plots
        py.figure()

        L = tmp.mean(axis=0).shape[0]
        meanMeanSimpleTarget = np.zeros( self.simpleT.shape )
        #~ meanMeanCSPTarget = np.zeros( self.conN*L/float(self.avrM) )
        meanMeanCSPTarget = np.zeros( self.CSP_t.shape )
        
        meanMeanSimpleNontarget = np.zeros( self.simpleT.shape )
        #~ meanMeanCSPNontarget = np.zeros( self.conN*L/float(self.avrM) )
        meanMeanCSPNontarget = np.zeros( self.CSP_t.shape )

        
        ## Plotting target ##
        for idx, tag in enumerate(self.trgTags):
            
            s = self.target[tag]
            
            meanCSPTarget = np.array([])
            for n in range(self.conN):
                tmp = self.prepareSignal( np.dot( self.P[:, n], s) )
                meanCSPTarget = np.concatenate((meanCSPTarget, tmp) )
            meanMeanCSPTarget += meanCSPTarget

            meanSimpleTarget = self.prepareSignal(s.mean(axis=0))
            meanMeanSimpleTarget += meanSimpleTarget

            
            py.subplot(2,2,1)
            py.plot(self.simpleT, meanSimpleTarget,'g-')
            #~ py.plot(meanSimpleTarget,'g-')

            py.subplot(2,2,2)
            py.plot(self.CSP_t, meanCSPTarget, 'g-')
            #~ py.plot(meanCSPTarget, 'g-')

        py.subplot(2,2,1)
        py.title("Simple mean target")
        py.plot(self.simpleT, meanMeanSimpleTarget/len(self.trgTags), 'r-')
        #~ py.plot(meanMeanSimpleTarget/len(self.trgTags), 'r-')
        
        py.subplot(2,2,2)
        py.title("CSP mean target")
        py.plot(self.CSP_t, meanMeanCSPTarget/len(self.trgTags), 'r-')
        for con in range(self.conN-1):
            py.axvline(con*(self.csp_time[1]-self.csp_time[0]))
        #~ py.plot( meanMeanCSPTarget/len(self.trgTags), 'r-')
        
        ## Plotting non target ##
        for idx, tag in enumerate(self.ntrgTags):
            
            s = self.nontarget[tag]
            meanCSPNontarget = np.array([])
            for n in range(self.conN):
                tmp = self.prepareSignal(np.dot( P[:,n], s))
                meanCSPNontarget = np.concatenate((meanCSPNontarget, tmp) )
            meanMeanCSPNontarget += meanCSPNontarget

            meanSimpleNontarget = self.prepareSignal(s.mean(axis=0))
            meanMeanSimpleNontarget += meanSimpleNontarget

            
            py.subplot(2,2,3)
            py.plot(self.simpleT, meanSimpleNontarget,'g-')
            #~ py.plot( meanSimpleNontarget,'g-')

            py.subplot(2,2,4)
            py.plot(self.CSP_t, meanCSPNontarget, 'g-')
            #~ py.plot( meanCSPNontarget, 'g-')

        py.subplot(2,2,3)
        py.title("Simple mean nontarget")
        py.plot(self.simpleT, meanMeanSimpleNontarget/len(self.ntrgTags), 'r-')
        #~ py.plot(meanMeanSimpleNontarget/len(self.ntrgTags), 'r-')

        py.subplot(2,2,4)
        py.title("CSP mean nontarget")
        py.plot(self.CSP_t, meanMeanCSPNontarget/len(self.ntrgTags), 'r-')
        for con in range(self.conN-1):
            py.axvline(self.csp_time[1] + con*(self.csp_time[1]-self.csp_time[0]))
        #~ py.plot(meanMeanCSPNontarget/len(self.ntrgTags), '-')

        py.show()
    
    def savePlotsD(self, dArrTotal, pVal):

        
        # Quick type check
        assert( type(pVal) == type(0.1) )
        assert( type(dArrTotal) == type({}) )
        
        
        # Determin what is the least number of blinks
        nBlink = 100
        for i in range(8):
            if nBlink > len(dArrTotal[i]): nBlink = len(dArrTotal[i])
        
        print "nBlink: ", nBlink
        # dMean is an array which has 8 columns and in rows mean value
        # after n blinks
        dMean = np.zeros((nBlink,8))
        for n in range(nBlink)[::-1]:
            for i in range(8):
                dMean[n][i] = dArrTotal[i][nBlink-n-1:].mean()
        
        print "dMean: ", dMean
        
        # "z" is treshold for difference in d and mean
        # "z" is calculated from pVal which is percentile
        z = st.norm.ppf(pVal)
        print "z: ", z
        for n in range(nBlink):
            py.subplot(2,(nBlink+1)/2, n+1)
            
            # This blok calculates:
            # - mean for all except one
            # - std for all except on
            # - treshold boundries for pVal significance
            m = []
            yMaxArr = []
            for i in range(8):
                tmpArr = np.delete(dMean[n], i)
                mVal = np.mean(tmpArr)
                stdVal = np.std(tmpArr)
                
                m.append(mVal)
                yMaxArr.append(mVal+stdVal*z)
        
            # we want to have label on just one block (the left one)
            if n == 0:
                py.ylabel('d')
            
            # plot mean for each field and for all without that one
            py.plot(dMean[n], 'ro')
            py.plot(m, 'bo')
            
            yMin, yMax = dMean[n].min(), dMean.max()
            ySpan = yMax - yMin
            yMin, yMax = yMin-ySpan*.1, yMax+ySpan*0.1
            ySpan = yMax - yMin
            
            py.title(n)
            py.ylim((yMin, yMax))
            py.xlim((-1,8))
            
            for idx in range(8):
                py.axvline(x=idx, ymin=(m[idx]-yMin)/ySpan, ymax=(yMaxArr[idx]-yMin)/ySpan)
        
        # save all blinks into one plot, then on hdd
        self.globalNCount += 1
        saveFile = "online_{0}.png".format(self.globalNCount)
        py.savefig(saveFile)
        py.cla()        
        py.clf()
        print "Zapisano obraz '{0}' w katalogu: {1}".format( saveFile, os.getcwd())
            
