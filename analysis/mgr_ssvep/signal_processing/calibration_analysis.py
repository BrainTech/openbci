# -*- coding: utf-8 -*-
import numpy as np



def cor(pattern, patterns_target, patterns_nontarget):
    target = {}
    nontarget = {}
    for pattern_freq in pattern.keys():
        target[pattern_freq] = [float(np.corrcoef(pattern[pattern_freq].pattern, pattern_test)[0][1]) for pattern_test in patterns_target[pattern_freq].pattern]
        nontarget[pattern_freq] = [float(np.corrcoef(pattern[pattern_freq].pattern, pattern_test)[0][1]) for pattern_test in patterns_nontarget[pattern_freq].pattern]
    return target, nontarget

def get_roc_auc_values(Target, Nontarget):  
    AUC = {} 
    ROC = {}
    for freq in Target.keys():
        target = np.array(Target[freq])
        nontarget = np.array(Nontarget[freq])
        target.sort()
        nontarget.sort()
        ro  = np.array([round(i,8) for i in np.linspace(min([min(target), min(nontarget)]), max([max(target), max(nontarget)]), 30)])
        SPC, TPR = [], []
        for i in ro:
            TP = len(target[target.searchsorted(i):])
            P = len(target)
            TN = len(nontarget[:nontarget.searchsorted(i)])
            N = len(nontarget)
            SPC.append(float(TN)/N)
            TPR.append(float(TP)/P)
        SPC = np.ones(len(SPC))-SPC
        ROC[freq] = [SPC, TPR]
        AUC[freq] = np.abs(sum([0.5*(TPR[i+1]+TPR[i])*(SPC[i+1]- SPC[i]) for i in range(len(SPC) -1)]))
        
    return ROC, AUC