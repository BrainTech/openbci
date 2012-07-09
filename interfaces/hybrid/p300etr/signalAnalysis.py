from scipy.signal import butter, buttord
from scipy.signal import filtfilt, lfilter
from scipy.signal import cheb2ord, cheby2
import numpy as np

import sys


class DataAnalysis(object):
    def __init__(self, fs):
        
        # Define constants
        self.fs = float(fs)
        self.initConst()
        
        # Set filter parameters
        self.set_lowPass_filter()
        self.set_highPass_filter()
    
        
    def initConst(self, avrM=1, conN=1, csp_time=[0,1]):
        self.avrM = avrM
        self.conN = conN
        self.csp_time = csp_time
        
        self.iInit, self.iFin = csp_time[0]*self.fs, csp_time[1]*self.fs
        
    def prepareSignal(self, s, avrM=None):
        """
        Prepare 1D signal for anylisis.
        """
        if avrM == None: avrM = self.avrM

        temp = s
        #~ temp = (temp-temp.mean())/temp.std()
        temp = self.filtrHigh(temp)
        temp = self.movingAvr(temp, avrM+1)
        #~ temp = self.filtrLow(temp)
        
        #~ temp = self.movingAvr(temp, 10)
        #~ temp = temp[self.iInit:self.iFin:avrM]
        if self.avrM == self.fs:
            pass
        else:
            temp = map(lambda i: temp[i], np.floor(np.linspace(self.csp_time[0], self.csp_time[1], self.avrM)*self.fs))
        
        return np.array(temp)
        
    def set_lowPass_filter(self, wp=20., ws=40., gpass=1., gstop=10.):
        Nq = self.fs/2.
        wp, ws = float(wp)/Nq, float(ws)/Nq
        gpass, gstop = float(gpass), float(gstop)
        N_filtr, Wn_filtr = buttord(wp, ws, gpass, gstop)
        self.b_L, self.a_L = butter(N_filtr, Wn_filtr, btype='low')

        self.N_L, self.Wn_L = N_filtr, Wn_filtr

    def set_lowPass_filter_ds(self, fs_new):
        Nq = self.fs/2.
        N_filtr, Wn_filtr = 2., fs_new/Nq
        self.b_L, self.a_L = butter(N_filtr, Wn_filtr, btype='low')

        self.N_L, self.Wn_L = N_filtr, Wn_filtr
        

    def set_highPass_filter(self, wp=5., ws=1., gpass=1., gstop=20.):
        #~ wp, ws = 10., 5.
        Nq = self.fs/2.
        wp, ws = float(wp)/Nq, float(ws)/Nq
        gpass, gstop = float(gpass), float(gstop)
        #~ N_filtr, Wn_filtr = buttord(wp, ws, gpass, gstop)
        N_filtr, Wn_filtr = 2, 1.5/Nq
        self.b_H, self.a_H = butter(N_filtr, Wn_filtr, btype='high')
        
        self.N_H, self.Wn_H = N_filtr, Wn_filtr
        
    
    def set_bandPass_filter(self):
        pass
    
    def printInfo(self):

        Nq = self.fs*0.5
        print "{0}".format(sys.argv[0])
        print "Low pass filter: "
        print "(N, Wn*Nq) = ( {}, {})".format(self.N_L, self.Wn_L*Nq)       
        print "High pass filter: "
        print "(N, Wn*Nq) = ( {}, {})".format(self.N_H, self.Wn_H*Nq)
        
    def filtrLow(self, s):
        return filtfilt(self.b_L, self.a_L, s)
        #~ return lfilter(self.b_L, self.a_L, s)

    def filtrHigh(self, s):
        #~ return lfilter(self.b_H, self.a_H, s)
        return filtfilt(self.b_H, self.a_H, s)
        
    def movingAvr(self, s, r):
        L, r = len(s), int(r)
        temp = np.zeros(L)
        temp[:r] = s[:r]
        for i in range(r):
            temp[r:L] += s[r-i:L-i]
        return temp/r

if __name__ == "__main__":
    sp = DataAnalysis(128.)
    sp.printInfo()
