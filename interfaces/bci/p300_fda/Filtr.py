from scipy.signal import filtfilt, butter, buttord
from scipy.signal import cheb2ord, cheby2
import numpy as np


class Filtr(object):
    def __init__(self, Fs):
        
        # Define constants
        self.Fs = float(Fs)
        
        # Set filter parameters
        self.set_lowPass_filter()
        self.set_highPass_filter()
        
        
    def set_lowPass_filter(self, wp=20., ws=30., gpass=1., gstop=20.):
        Nq = self.Fs/2.
        wp, ws = wp/Nq, ws/Nq
        N_filtr, Wn_filtr = buttord(wp, ws, gpass, gstop)
        self.b_L, self.a_L = butter(N_filtr, Wn_filtr, btype='low')

    def set_highPass_filter(self, wp=1., ws=0.1, gpass=1., gstop=10.):
        Nq = self.Fs/2.
        wp, ws = wp/Nq, ws/Nq
        N_filtr, Wn_filtr = buttord(wp, ws, gpass, gstop)
        self.b_H, self.a_H = butter(N_filtr, Wn_filtr, btype='high')
            
    def filtrLow(self, s):
        return filtfilt(self.b_L, self.a_L, s)

    def filtrHigh(self, s, axis=-1):
        return filtfilt(self.b_H, self.a_H, s)
        
    def movingAvr(s,r):
        temp = s.copy()
        for n in range(r,len(s)):
            temp[n] = s[n-r:n].sum()/r
        return temp
