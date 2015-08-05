# -*- coding: utf-8 -*-
import numpy as np



def cor(patterns_trenning, patterns_test_target, patterns_test_nontarget):
    target = {}
    nontarget = {f:[] for f in patterns_trenning.keys()}
    for pattern_freq in patterns_trenning.keys():
        target[pattern_freq] = [float(np.corrcoef(patterns_trenning[pattern_freq], pattern_test)[0][1]) for pattern_test in patterns_test_target[pattern_freq]]
        for f, pattern_test in patterns_test_nontarget[pattern_freq]:
            nontarget[pattern_freq].append([float(np.corrcoef(patterns_trenning[f_], p)[0][1]) for f_, p in zip(f, pattern_test)])
        nontarget[pattern_freq] = sum(nontarget[pattern_freq], [])

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