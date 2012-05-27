#!/usr/bin/python
# coding: UTF-8
import numpy as np
import pylab as py  

import scipy.io
import scipy.stats as st
from signalAnalysis import  DataAnalysis
import sys, os, time


class P300_draw(object):
    def __init__(self, fs=128.):
        
        self.fs = fs
        self.globalNCount = 0
        
        self.defineMethods()
    
    def defineMethods(self):
        # Declare methods
        self.sp = DataAnalysis(self.fs)
        self.sp.initConst(avrM=self.fs)

        self.sp_ds = DataAnalysis(self.fs)
        
    def setCalibration(self, target, nontarget):
        # Sorting tags... (for no real reason)

        # Setting arrays/dicts
        self.target = target 
        self.nontarget = nontarget
        
        self.trgTrials = target.shape[0]
        self.ntrgTrials = nontarget.shape[0]

        
    def setTimeLine(self, conN, avrM=None, csp_time=[0,1]):
        self.conN = conN
        self.csp_time = csp_time
        if avrM == None: self.avrM = self.fs
        else: self.avrM = avrM
        
    def setCSP(self, P):
        self.P = P
        
    def plotSignal(self, savefile=None):
        
        py.clf()
        py.cla()

        # Determine size
        tmp = self.target[0]
        L = self.sp.prepareSignal(tmp[0]).shape[0]
        
        # P matrix
        if self.P==None: self.P = np.ones(tmp.shape)
        P = self.P

        # Set time limits
        self.simple_time = np.linspace(0, 1, L)

        # Create arrays
        meanMeanSimpleTarget = np.zeros( L )
        meanMeanCSPTarget = np.zeros( self.conN*L )
        
        meanMeanSimpleNontarget = np.zeros( L )
        meanMeanCSPNontarget = np.zeros( self.conN*L )

        ## New plotting figure
        #~ py.figure()

        ## Plotting target ##
        for idx in range(self.trgTrials):
            
            s = self.target[idx]
            meanCSPTarget = np.array([])

            meanSimpleTarget = self.sp.prepareSignal(s.mean(axis=0))
            meanMeanSimpleTarget += meanSimpleTarget

            py.subplot(2,1+self.conN,1)
            py.plot(self.simple_time, meanSimpleTarget, 'g-')

            for con in range(self.conN):
                tmp = self.sp.prepareSignal(np.dot( P[:,con], s))
                py.subplot(2,1+self.conN,2+con)
                py.plot(self.simple_time, tmp, 'g-')

                meanCSPTarget = np.concatenate((meanCSPTarget, tmp) )
            meanMeanCSPTarget += meanCSPTarget

            
        py.subplot(2,1+self.conN,1)
        py.title("Simple mean target")
        py.plot(self.simple_time, meanMeanSimpleTarget/self.trgTrials, 'r-')
            
        for con in range(self.conN):
                py.subplot(2,1+self.conN,2+con)
                py.title("CSP mean target vec " +str(con+1))
                py.plot(self.simple_time, meanMeanCSPTarget[con*L:(con+1)*L]/self.trgTrials, 'r-')

        #########################
        ## Plotting non target ##
        for idx in range(self.ntrgTrials):
            
            s = self.nontarget[idx]

            meanSimpleNontarget = self.sp.prepareSignal(s.mean(axis=0), 1)
            meanMeanSimpleNontarget += meanSimpleNontarget


            py.subplot(2,1+self.conN,self.conN+2)
            py.plot(self.simple_time, meanSimpleNontarget,'g-')

            meanCSPNontarget = np.array([])
            for con in range(self.conN):
                tmp = self.sp.prepareSignal(np.dot( P[:,con], s))
                meanCSPNontarget = np.concatenate((meanCSPNontarget, tmp) )
                py.subplot(2,1+self.conN,self.conN+3+con)
                py.plot(self.simple_time, tmp, 'g-')

            meanMeanCSPNontarget += meanCSPNontarget
            
        py.subplot(2,1+self.conN,self.conN+2)
        py.title("Simple mean nontarget")
        py.plot(self.simple_time, meanMeanSimpleNontarget/self.ntrgTrials, 'r-')

        for con in range(self.conN):
            py.subplot(2,1+self.conN,self.conN+3+con)
            py.title("CSP mean nontarget vec " +str(con+1))
            py.plot(self.simple_time, meanMeanCSPNontarget[con*L:(con+1)*L]/self.ntrgTrials, 'r-')

        if savefile:
            py.savefig(savefile, dpi=150)

        ## Plotting Diff
        py.figure()        
        
        meanTarget = meanMeanSimpleTarget/self.trgTrials
        meanNontarget = meanMeanSimpleNontarget/self.ntrgTrials
        
        meanCSPTarget = meanMeanCSPTarget/self.trgTrials
        meanCSPNontarget = meanMeanCSPNontarget/self.ntrgTrials
        
        py.subplot(1, 1+self.conN,1)
        py.title("Diff simple mean")
        py.plot(self.simple_time, meanTarget-meanNontarget, 'r-')
        
        for con in range(self.conN):
            py.subplot(1,1+self.conN,2+con)
            py.title("Diff CSP mean vec " + str(con+1))
            py.plot(self.simple_time, (meanCSPTarget-meanCSPNontarget)[con*L:(con+1)*L], 'r-')
            
        if savefile:
            py.savefig(savefile + "_diff", dpi=150)
        else:
            py.show()
            
        py.clf()
        py.cla()
        
    def plotSignal_ds(self, savefile=None):
        
        py.clf()
        py.cla()
        
        L = self.avrM

        if self.P==None: self.P = np.ones(tmp.shape)
        P = self.P

        # Create buffers
        meanMeanSimpleTarget = np.zeros( L )
        meanMeanCSPTarget = np.zeros( self.conN*L )
        
        meanMeanSimpleNontarget = np.zeros( L )
        meanMeanCSPNontarget = np.zeros( self.conN*L )

        tMin, tMax = self.csp_time[0], self.csp_time[1]
        self.sp_ds.initConst(self.avrM, self.conN, self.csp_time)
        self.simple_time_ds = np.linspace(tMin, tMax, self.avrM)
        
        # X axis limits
        dx = self.csp_time[1] - self.csp_time[0]
        xMin = self.csp_time[0] - 0.25*dx
        xMax = self.csp_time[1] + 0.25*dx
        
        #######################
        ##  Plotting target  ##
        for idx in range(self.trgTrials):
            
            s = self.target[idx]
            meanCSPTarget = np.array([])
            
            meanSimpleTarget = self.sp_ds.prepareSignal(s.mean(axis=0))
            meanMeanSimpleTarget += meanSimpleTarget

            py.subplot(2,1+self.conN,1)
            py.plot(self.simple_time_ds, meanSimpleTarget,'g.')
                
            for con in range(self.conN):
                tmp = self.sp_ds.prepareSignal(np.dot( P[:,con], s))
                py.subplot(2,1+self.conN,2+con)
                py.plot(self.simple_time_ds, tmp, 'g.')
                
                meanCSPTarget = np.concatenate((meanCSPTarget, tmp) )
            meanMeanCSPTarget += meanCSPTarget

        py.subplot(2,1+self.conN,1)
        py.title("Simple mean target")
        py.plot(self.simple_time_ds, meanMeanSimpleTarget/self.trgTrials, 'ro')
        py.xlim(xMin, xMax)
        
        for con in range(self.conN):
            py.subplot(2,1+self.conN,2+con)
            py.title("CSP mean target vec" +str(con+1))
            py.plot(self.simple_time_ds, meanMeanCSPTarget[con*self.avrM:(con+1)*self.avrM]/self.trgTrials, 'ro')
            py.xlim(xMin, xMax)
        
        #########################
        ## Plotting non target ##
        for idx in range(self.ntrgTrials):
            
            s = self.nontarget[idx]

            meanSimpleNontarget = self.sp_ds.prepareSignal(s.mean(axis=0))
            meanMeanSimpleNontarget += meanSimpleNontarget

            
            py.subplot(2,1+self.conN,self.conN+2)
            py.plot(self.simple_time_ds, meanSimpleNontarget,'g.')

            meanCSPNontarget = np.array([])
            for con in range(self.conN):
                tmp = self.sp_ds.prepareSignal(np.dot( P[:,con], s))
                meanCSPNontarget = np.concatenate((meanCSPNontarget, tmp) )
                py.subplot(2,1+self.conN,self.conN+3+con)
                py.plot(self.simple_time_ds, tmp, 'g.')

            meanMeanCSPNontarget += meanCSPNontarget

        py.subplot(2,1+self.conN,self.conN+2)
        py.title("Simple mean nontarget")
        py.plot(self.simple_time_ds, meanMeanSimpleNontarget/self.ntrgTrials, 'ro')
        py.xlim(xMin, xMax)
        
        for con in range(self.conN):
            py.subplot(2,1+self.conN,self.conN+3+con)
            py.title("CSP mean nontarget vec " +str(con+1))
            py.plot(self.simple_time_ds, meanMeanCSPNontarget[con*self.avrM:(con+1)*self.avrM]/self.ntrgTrials, 'ro')
            py.xlim(xMin, xMax)

        if savefile:
            py.savefig(savefile, dpi=150)
        
        
        ## Plotting Diff
        py.figure()        
        
        meanTarget = meanMeanSimpleTarget/self.trgTrials
        meanNontarget = meanMeanSimpleNontarget/self.ntrgTrials
        
        meanCSPTarget = meanMeanCSPTarget/self.trgTrials
        meanCSPNontarget = meanMeanCSPNontarget/self.ntrgTrials
        
        py.subplot(1, 1+self.conN,1)
        py.title("Diff simple mean")
        py.plot(self.simple_time_ds, meanTarget-meanNontarget, 'ro')
        py.xlim(xMin, xMax)
        
        for con in range(self.conN):
            py.subplot(1,1+self.conN,2+con)
            py.title("Diff CSP mean vec " + str(con+1))
            py.plot(self.simple_time_ds, (meanCSPTarget-meanCSPNontarget)[con*self.avrM:(con+1)*self.avrM], 'ro')
            py.xlim(xMin, xMax)
        
        if savefile:
            py.savefig(savefile + '_diff', dpi=150)
        else:
            py.show()
            
        py.clf()
        py.cla()
    
    def savePlotsD(self, dArrTotal, pVal, savefile=None):

        
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
        if savefile == None:
            savefile = "online_{0}.png".format(self.globalNCount)
        py.savefig(savefile, dpi=150)
        py.cla()        
        py.clf()
        print "Zapisano obraz '{0}' w katalogu: {1}".format( savefile, os.getcwd())
            
    def plotDistribution(self, dTarget, dNontarget, savefile=None):
        """
        Takes 1D numpy arrays of d values for target and nontarget.
        Plots and saves their histograms to file.
        """
        bins = 20
        
        py.subplot(2,2,1)
        py.title("Target distribution")
        py.hist(dTarget, bins)
        py.axvline(dTarget.mean(), color='r')
        py.xlabel("d values")
        py.ylabel("Quantity")
        
        py.subplot(2,2,2)
        py.title("Nontarget distribution")
        py.hist(dNontarget, bins)
        py.axvline(dNontarget.mean(), color='r')
        py.xlabel("d values")
        py.ylabel("Quantity")

        py.subplot(2,1,2)
        py.title("Target/Nontarget distribution")
        py.hist(np.append(dTarget,dNontarget), bins)
        py.axvline(dTarget.mean(), color='r')
        py.axvline(dNontarget.mean(), color='r')
        py.xlabel("d values")
        py.ylabel("Quantity")

        if savefile == None:
            savefile = "distrib_{0}.png".format(self.globalNCount)
        self.globalNCount += 1
        
        py.savefig(savefile, dpi=150)
        
        py.show()
