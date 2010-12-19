#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from data_storage import read_manager
import analysis_offline
class ReadSignal(object):
    def __init__(self, files):
        self.files = files
    def process(self, *whatever):
        mgr = read_manager.ReadManager(self.files['info'],
                                       self.files['data'],
                                       self.files['tags'])
        return [mgr]
    def __repr__(self):
        return str({"CLASS": self.__class__.__name__,
                   "FILES":str(self.files)})
                        

class ExcludeChannels(object):
    def __init__(self, channels):
        self.channels = channels

    def process(self, mgrs):
        new_mgrs = []
        for i_mgr in mgrs:
            new_mgrs.append(analysis_offline.exclude_channels(i_mgr, self.channels))
        return new_mgrs

    def __repr__(self):
        return str({"CLASS": self.__class__.__name__,
                    "CHANNELS": str(self.channels)})

class LeaveChannels(object):
    def __init__(self, channels):
        self.channels = channels

    def process(self, mgrs):
        new_mgrs = []
        for i_mgr in mgrs:
            new_mgrs.append(analysis_offline.leave_channels(i_mgr, self.channels))
        return new_mgrs

    def __repr__(self):
        return str({"CLASS": self.__class__.__name__,
                    "CHANNELS": str(self.channels)})
        


class Montage(object):
    def __init__(self, montage_type, **montage_params):
        self.montage_type = montage_type
        self.montage_params = montage_params
    def process(self, mgrs):
        new_mgrs = []
        for i_mgr in mgrs:
            new_mgrs.append(analysis_offline.montage(i_mgr, self.montage_type, **self.montage_params))
        return new_mgrs
    def __repr__(self):
        return str({"CLASS": self.__class__.__name__,
                    "montage_type": self.montage_type})

        






class PrepareTrainSet(object):
    def process(self, data):
        pass
    
class SVM(object):
    def __init__(self, C):
        self.s = svm.SVM(C=C)
    def process(self, data):
        return self.s.stratifiedCV(data, 5).getBalancedSuccessRate()
    def __repr__(self):
        return str({"CLASS": self.__class__.__name__,
                    "C": str(self.s.C)})

















            
class Filter(object):
    def __init__(**p_args):
        pass
    def process(p_mgrs):
        return p_mgrs



class Donwnsample(object):
    def __init__(self, new_sampling=None, leave_every=None):
        #albo new_sampling albo leave_every 
        pass
    def process(self, p_mgrs):
        return p_mgrs


class LinearTransform(object):
    def __init__(self, **p_args):
        pass
    def process(self, p_mgrs):
        return p_mgrs


class ToMvTransform(object):
    def __init__(self):
        pass
    def process(self, p_mgrs):
        pass
        #dla każdego mgr-a:
        # pobierz jego gain i offset i zrób jego dane danymi w mikrowoltach

class Normalise(object):
    def __init__(self, norm=2):
        pass
    def process(self, p_mgrs):
        pass
        #dla każdego mgr-a:
        # po każdym kanale: podziel (chyba) kanał przez jego normę



class Average(object):
    def __init__(self, **args):
        pass
    def process(self, p_mgrs):
        pass
                
