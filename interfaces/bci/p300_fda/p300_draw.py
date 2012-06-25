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

        # Create buffers
        allCSPTrg = np.empty( (self.conN, self.target.shape[0], L))
        allCSPNtrg = np.empty( (self.conN, self.nontarget.shape[0], L))
        
        allMeanCSPTrg = np.empty( (self.conN, L))
        allMeanCSPNtrg = np.empty( (self.conN, L))
        
        # Plot simple means
        productMeanTrg = self.target.mean(axis=1)
        productMeanNtrg = self. nontarget.mean(axis=1)

        analProductMeanTrg = np.array(map( lambda sig: self.sp.prepareSignal(sig), productMeanTrg))
        analProductMeanNtrg = np.array(map( lambda sig: self.sp.prepareSignal(sig), productMeanNtrg))


        ##
        timeArr = np.array(self.simple_time.tolist()*analProductMeanTrg.shape[0]).reshape((-1,L))
        py.subplot(2, 1+self.conN, 1) # 1st row
        py.title("Mean target")
        py.plot(np.transpose(timeArr), np.transpose(analProductMeanTrg),'r-')
        py.plot(self.simple_time, analProductMeanTrg.mean(axis=0),'g-')


        ##
        timeArr = np.array(self.simple_time.tolist()*analProductMeanNtrg.shape[0]).reshape((-1,L))
        py.subplot(2, 1+self.conN, 2+self.conN) # 2nd row
        py.title("Mean nontarget")
        py.plot(np.transpose(timeArr), np.transpose(analProductMeanNtrg),'r-')
        py.plot(self.simple_time, analProductMeanNtrg.mean(axis=0),'g-')

        #######################
        ##  Plotting target  ##
        # Depending how many eigenvectors one want's to consider
        # from CSP,
        for con in range(self.conN):
            # Dot product over all channels (CSP filter) and returns
            # array of (trials, data) shape.
            productCSPTrg = np.dot( self.P[:,con], self.target)
            productCSPNtrg = np.dot( self.P[:,con], self.nontarget)

            # Each data signal is analysed: filtred, downsized...
            analProductCSPTrg = np.array(map( lambda sig: self.sp.prepareSignal(sig), productCSPTrg))
            analProductCSPNtrg = np.array(map( lambda sig: self.sp.prepareSignal(sig), productCSPNtrg))
            
            allCSPTrg[con] = analProductCSPTrg
            allCSPNtrg[con] = analProductCSPNtrg
            
            allMeanCSPTrg[con] = analProductCSPTrg.mean(axis=0)
            allMeanCSPNtrg[con] = analProductCSPNtrg.mean(axis=0)

            ## PLOT
            timeArr = np.array(self.simple_time.tolist()*analProductCSPTrg.shape[0]).reshape((-1,L))
            py.subplot(2,1+self.conN,2+con)
            py.title("CSP mean target vec" +str(con+1))
            py.plot(np.transpose(timeArr), np.transpose(analProductCSPTrg), 'r-')
            py.plot(self.simple_time, allMeanCSPTrg[con], 'g-')

            ## PLOT
            timeArr = np.array(self.simple_time.tolist()*analProductCSPNtrg.shape[0]).reshape((-1,L))
            py.subplot(2,1+self.conN,self.conN+1+2+con)
            py.title("CSP mean nontarget vec" +str(con+1))
            py.plot(np.transpose(timeArr), np.transpose(analProductCSPNtrg), 'r-')
            py.plot(self.simple_time, allMeanCSPNtrg[con], 'g-')


        if savefile:
            py.savefig(savefile, dpi=150)

        
        ## Plotting Diff
        py.figure()        
        
        meanTarget = analProductMeanTrg.mean(axis=0)
        meanNontarget = analProductMeanNtrg.mean(axis=0)
        
        py.subplot(1, 1+self.conN,1)
        py.title("Diff simple mean")
        py.plot(self.simple_time, meanTarget-meanNontarget, 'r-')
        
        print "self.simple_time.shape: ", self.simple_time.shape
        print "allMeanCSPTrg[0].shape: ", allMeanCSPTrg[0].shape
        print "allMeanCSPNtrg[0].shape: ", allMeanCSPNtrg[0].shape
        
        for con in range(self.conN):
        #~ for con in range(1):
            py.subplot(1,1+self.conN,2+con)
            py.title("Diff CSP mean vec " + str(con+1))
            py.plot(self.simple_time, allMeanCSPTrg[con]-allMeanCSPNtrg[con], 'r-')
        
        if savefile:
            py.savefig(savefile + '_diff', dpi=150)
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
        allCSPTrg = np.empty( (self.conN, self.target.shape[0], self.avrM))
        allCSPNtrg = np.empty( (self.conN, self.nontarget.shape[0], self.avrM))
        
        allMeanCSPTrg = np.empty( (self.conN, self.avrM))
        allMeanCSPNtrg = np.empty( (self.conN, self.avrM))
        
        # Time
        tMin, tMax = self.csp_time[0], self.csp_time[1]
        self.sp_ds.initConst(self.avrM, self.conN, self.csp_time)
        self.simple_time_ds = np.linspace(tMin, tMax, self.avrM)
        
        # X axis limits
        dx = self.csp_time[1] - self.csp_time[0]
        xMin = self.csp_time[0] - 0.25*dx
        xMax = self.csp_time[1] + 0.25*dx
        
        # Plot simple means
        productMeanTrg = self.target.mean(axis=1)
        productMeanNtrg = self. nontarget.mean(axis=1)

        analProductMeanTrg = np.array(map( lambda sig: self.sp_ds.prepareSignal(sig), productMeanTrg))
        analProductMeanNtrg = np.array(map( lambda sig: self.sp_ds.prepareSignal(sig), productMeanNtrg))
        
        ## PLOT
        timeArr = np.array(self.simple_time_ds.tolist()*analProductMeanTrg.shape[0]).reshape((-1,self.avrM))
        py.subplot(2, 1+self.conN, 1) # 1st row
        py.title("Mean target")
        py.plot(self.simple_time_ds, analProductMeanTrg.mean(axis=0),'g-')
        py.plot(np.transpose(timeArr), np.transpose(analProductMeanTrg),'r.')
        py.xlim(xMin, xMax)

        ## PLOT
        timeArr = np.array(self.simple_time_ds.tolist()*analProductMeanNtrg.shape[0]).reshape((-1,self.avrM))
        py.subplot(2, 1+self.conN, 2+self.conN) # 2nd row
        py.title("Mean nontarget")
        py.plot(np.transpose(timeArr), np.transpose(analProductMeanNtrg),'r.')
        py.plot(self.simple_time_ds, analProductMeanTrg.mean(axis=0),'g')
        py.xlim(xMin, xMax)
        

        #######################
        ##  Plotting target  ##
        # Depending how many eigenvectors one want's to consider
        # from CSP,
        for con in range(self.conN):
            # Dot product over all channels (CSP filter) and returns
            # array of (trials, data) shape.
            productCSPTrg = np.dot( self.P[:,con], self.target)
            productCSPNtrg = np.dot( self.P[:,con], self.nontarget)

            # Each data signal is analysed: filtred, downsized...
            analProductCSPTrg = np.array(map( lambda sig: self.sp_ds.prepareSignal(sig), productCSPTrg))
            analProductCSPNtrg = np.array(map( lambda sig: self.sp_ds.prepareSignal(sig), productCSPNtrg))
            
            allCSPTrg[con] = analProductCSPTrg
            allCSPNtrg[con] = analProductCSPNtrg
            
            allMeanCSPTrg[con] = analProductCSPTrg.mean(axis=0)
            allMeanCSPNtrg[con] = analProductCSPNtrg.mean(axis=0)

            ## PLOT
            timeArr = np.array(self.simple_time_ds.tolist()*analProductCSPTrg.shape[0]).reshape((-1,self.avrM))
            py.subplot(2,1+self.conN,2+con)
            py.title("CSP mean target vec" +str(con+1))
            py.plot(np.transpose(timeArr), np.transpose(analProductCSPTrg), 'r.')
            py.plot(self.simple_time_ds, allMeanCSPTrg[con], 'g-')
            py.xlim(xMin, xMax)
            
            ## PLOT
            timeArr = np.array(self.simple_time_ds.tolist()*analProductCSPNtrg.shape[0]).reshape((-1,self.avrM))
            py.subplot(2,1+self.conN,self.conN+1+2+con)
            py.title("CSP mean nontarget vec" +str(con+1))
            py.plot(np.transpose(timeArr), np.transpose(analProductCSPNtrg), 'r.')
            py.plot(self.simple_time_ds, allMeanCSPNtrg[con], 'g-')
            py.xlim(xMin, xMax)
        
        
        if savefile:
            py.savefig(savefile, dpi=150)
        
        
        ## Plotting Diff
        py.figure()        
        
        meanTarget = analProductMeanTrg.mean(axis=0)
        meanNontarget = analProductMeanNtrg.mean(axis=0)
        
        py.subplot(1, 1+self.conN,1)
        py.title("Diff simple mean")
        py.plot(self.simple_time_ds, meanTarget-meanNontarget, 'r-')
        py.xlim(xMin, xMax)
        
        for con in range(self.conN):
        #~ for con in range(1):
            py.subplot(1,1+self.conN,2+con)
            py.title("Diff CSP mean vec " + str(con+1))
            py.plot(self.simple_time_ds, allMeanCSPTrg[con]-allMeanCSPNtrg[con], 'r-')
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
            
    def plotDistribution(self, dTarget, dNontarget, savefile=None, show=None):
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
        py.cla()        
        py.clf()        
        if show:
            py.show()
