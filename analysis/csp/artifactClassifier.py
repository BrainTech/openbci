# coding: UTF-8

import pylab as py
import numpy as np
import scipy.linalg as sl
from numpy.fft import fft,fftshift,fftfreq
from scipy.stats import chi2
from numpy import matrix, linalg
from signalParser import signalParser    
from Filtr import Filtr
import sys

def periodogram(s):
    '''peiodogram sygnaÅu s
    okno - synaÅ bÄdzie przez nie przemnoÅ¼ony w czasie
    samplingFrequency - czÄstoÅÄ prÃ³bkowania'''

    N = s.shape[0]
    window = np.hamming(N)

    #~ for i in xrange(s.shape[1]):
        #~ s[:,i] = window*s[:,i]
    s = (window*(s.T)).T

    S = fft(s,N,axis=0)#/np.sqrt(N_fft)
    P = S*S.conj()/np.sum(window**2)
    
    P = P.real # P i tak ma zerowe wartoÅÄi urojone, ale trzeba wykonaÄ konwersjÄ typÃ³w
    return np.log10(P)


def integratePowerSpectrumDensity(signalPowerSpectrumDensity, frequencyBands, dF):
    '''CaÅkuj gÄstoÅÄ widmowÄ w okreÅlonych pasmach'''
    '''Na razie bÄdÄ zakÅÄdaÅ, Å¼e cechy pochdzÄ tylko z pierwszego, najlepszego kanÅau po CSP'''

    # Reshaping so that noOfTrials is always a number
    numberOfStepsInFrequency = signalPowerSpectrumDensity.shape[0]
    signalPowerSpectrumDensity = signalPowerSpectrumDensity.reshape((numberOfStepsInFrequency,-1))

    numberOfTrials = signalPowerSpectrumDensity.shape[1]    
    numberOfFrequencyBands = frequencyBands.shape[0]

    featuresVector = np.zeros((numberOfTrials,numberOfFrequencyBands))

    for frequencyBandNumber in range(numberOfFrequencyBands):
        startBandIndex, lastBandIndex = np.floor(frequencyBands[frequencyBandNumber]/dF)
        
        featuresVector[:,frequencyBandNumber] = np.sum(signalPowerSpectrumDensity[startBandIndex:lastBandIndex,:],0)
        
    return featuresVector


def chi2inv(x, df):
    chi2cdf = 1.0/chi2.cdf(x, df)
    chi2cdf = 7.8147;
    return chi2cdf
#1./chi2.cdf(1-x, df)
    
def mh(vec, vecSet):
    mi = vecSet.mean(axis=0)
    
    C = np.cov(vecSet, rowvar=0)
    invC = matrix(C).I

    x = vec-mi
    d = np.dot(np.dot(x,invC), x.T)
    
    return d
   
def isVectorCloseToSet(vectorSet, vector):
    vectorSet = matrix(vectorSet)
    vector = matrix(vector)


    confidenceLevel = 0.95
    answer = True
    dimention = vector.shape[1]
    unknowVectorMinimalDistance = mh(vector,vectorSet)


    criticalDistance = chi2inv(confidenceLevel, dimention)

    if (unknowVectorMinimalDistance > criticalDistance):
       answer = False
    
    return answer
       
   
            
def artifactsCalibration(eegSignal,samplingFrequency):

    numberOfFrequencyBands = 3
    frequencyBands = np.zeros([numberOfFrequencyBands, 2])
    frequencyBands[0] = np.array([1, 7]) # poczatek i koniec dane poasma w Hz
    frequencyBands[1] = np.array([7, 14]) # poczatek i koniec dane poasma w Hz
    frequencyBands[2] = np.array([15, 45]) # poczatek i koniec dane poasma w Hz
    
    numberOfChannels, numberOfSamples, numberOfTrials = eegSignal.shape
    dF = (1.0*samplingFrequency)/numberOfSamples

    # Averaging over all chanells
    meanSignal = np.mean(eegSignal,axis = 0)
    
    # Filter
    for i in range(meanSignal.shape[1]):
        meanSignal[:,i] = filtr.filtrHigh(meanSignal[:,i])
    
    bufforLength = int(0.5*samplingFrequency)
    lagOfBuffor  = int(bufforLength/2.0)
    numberOfInternalWindows = (int)((1.0*(numberOfSamples - bufforLength))/lagOfBuffor)

    estimateFeaturesSet = np.zeros([numberOfInternalWindows,numberOfFrequencyBands]);

    for windowNumber in range(numberOfInternalWindows):
        powerSpectrumDensity = periodogram(meanSignal[windowNumber*lagOfBuffor  : windowNumber*lagOfBuffor + bufforLength,:])
        tmpEstimateFeaturesSet = integratePowerSpectrumDensity(powerSpectrumDensity,frequencyBands,dF)
        if windowNumber==0:
            estimateFeaturesSet = tmpEstimateFeaturesSet
        else:
            estimateFeaturesSet = np.concatenate((estimateFeaturesSet,tmpEstimateFeaturesSet),0)
        

    return estimateFeaturesSet, frequencyBands
    
def artifactsClasifier(eegSignal, estimateFeaturesSet, frequencyBands, samplingFrequency):
    
    
    numberOfChannels, numberOfSamples = eegSignal.shape
    dF = (1.0*samplingFrequency)/numberOfSamples
   

    # Averaging over all chanells
    meanSignal = np.mean(eegSignal,axis = 0)

    meanSignal = filtr.filtrHigh(meanSignal)
       
    bufforLength = int(0.5*samplingFrequency)    
    lagOfBuffor  = int(bufforLength/2.0)
    numberOfInternalWindows = (int)((1.0*(numberOfSamples - bufforLength))/lagOfBuffor)
       
    for windowNumber in range(numberOfInternalWindows):        
        powerSpectrumDensity = periodogram(meanSignal[windowNumber*lagOfBuffor  : windowNumber*lagOfBuffor + bufforLength])
        estimateFeaturesVector = integratePowerSpectrumDensity(powerSpectrumDensity,frequencyBands,dF)
        if(isVectorCloseToSet(estimateFeaturesSet,estimateFeaturesVector)==False):
            return False
        
    return True

def sin(f = 1, T = 1, Fs = 128, phi =0 ):
    '''sin o zadanej czÄstoÅci (w Hz), dÅugoÅci, fazie i czÄstoÅci prÃ³bkowania
    DomyÅlnie wytwarzany jest sygnaÅ reprezentujÄcy 
    1 sekundÄ sinusa o czÄstoÅci 1Hz i zerowej fazie prÃ³bkowanego 128 Hz
    '''
 
    dt = 1.0/Fs
    t = np.arange(0,T,dt)
    s = np.sin(2*np.pi*f*t + phi)
    return s


if __name__ == "__main__":

    fnCalibration   = "dawid1.obci"
    fnClasification = "dawid2.obci"
    #~ CHANNELS = "PO7,O1,Oz,O2,PO8,PO3,PO4,Pz,Cz".split(',')
    CHANNELS = "PO7,O1,O2,PO8,PO3,PO4,Pz,Cz".split(',')
    REF_CHANNEL = ["Pz"]
    chL = len(CHANNELS)
    
    sigPars = signalParser(fnCalibration)
    refSig = sigPars.extract_channel(REF_CHANNEL)
    eegSig = sigPars.extract_channel(CHANNELS)
    eegSigCalibration = eegSig - refSig

    sigPars = signalParser(fnClasification)
    refSig = sigPars.extract_channel(REF_CHANNEL)
    eegSig = sigPars.extract_channel(CHANNELS)
    eegSigClassification = eegSig - refSig

    #~ eegSig = eegSig - np.mean(eegSig, axis=1)
        
    Fs = 128.0
    filtr = Filtr(Fs)
    filtr.set_lowPass_filter()
    filtr.set_highPass_filter()
        
    sampleCountCalibration = 14908
    lag = 0.25*Fs
    windowLength = 2.0*Fs
    nWindow = int((sampleCountCalibration - windowLength)/lag)
    
    dataL = np.zeros([chL, windowLength, int(nWindow)])
    
    for i in range(int(nWindow)):
        dataL[:,:,i] = eegSigCalibration[:,int((lag-1)*i):int((lag-1)*i)+windowLength]

    estimateFeaturesSet, frequencyBands = artifactsCalibration(dataL, 128)

    sampleCountClassification = 14832
    lag = 0.25*Fs
    windowLength = 2.0*Fs
    nWindow = int((sampleCountClassification - windowLength)/lag)
    
    
    nTrue = 0
    data_last = None
    for i in range(int(nWindow)):
        dataClassification = eegSigClassification[:,(lag-1)*i:(lag-1)*i+windowLength]
        print i, artifactsClasifier(dataClassification, estimateFeaturesSet, frequencyBands, 128)
        py.plot(dataClassification[0,:])
        py.show()
