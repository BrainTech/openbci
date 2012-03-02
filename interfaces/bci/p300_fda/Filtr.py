from scipy.signal import filtfilt, butter, buttord
from scipy.signal import cheb2ord, cheby2


class Filtr(object):
    def __init__(self, Fs):
        
        # Define constants
        self.Fs = float(Fs)
        
        # Set filter parameters
        self.set_lowPass_filter()
        self.set_highPass_filter()
        
        
    def set_lowPass_filter(self):
        Nq = self.Fs/2.
        wp, ws = 20./Nq, 30./Nq
        gpass, gstop = 1., 20.
        N_filtr, Wn_filtr = buttord(wp, ws, gpass, gstop)
        self.b_L, self.a_L = butter(N_filtr, Wn_filtr, btype='low')

    def set_highPass_filter(self):
        Nq = self.Fs/2.
        wp, ws = 1./Nq, 0.1/Nq
        gpass, gstop = 1., 10.
        N_filtr, Wn_filtr = buttord(wp, ws, gpass, gstop)
        self.b_H, self.a_H = butter(N_filtr, Wn_filtr, btype='high')
            
    def filtrLow(self, s):
        return filtfilt(self.b_L, self.a_L, s)

    def filtrHigh(self, s):
        return filtfilt(self.b_H, self.a_H, s)
        
    def movingAvr(s,r):
        temp = s.copy()
        for n in range(r,len(s)):
            temp[n] = s[n-r:n].sum()/r
        return temp
