#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from data_storage import read_manager
import analysis_offline
class ReadSignal(object):
    def __init__(self, files):
        self.files = files
    def process(self, files=None):
        if not self.files is None:
            files = self.files
        mgrs = []
        for f in files:
            mgrs.append(read_manager.ReadManager(f['info'],
                                                 f['data'],
                                                 f['tags']))
        return mgrs
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
                    "montage_type": self.montage_type,
                    "montage_params": self.montage_params})

        

class Normalize(object):
    def __init__(self, norm=2):
        self.norm = norm
    def process(self, mgrs):
        new_mgrs = []
        for i_mgr in mgrs:
            new_mgrs.append(analysis_offline.normalize(i_mgr, self.norm))
        return new_mgrs
    def __repr__(self):
        return str({"CLASS": self.__class__.__name__,
                    "norm": self.norm})




class PrepareTrainSet(object):
    def __init__(self, **whatever):
        pass
    def process(self, mgrs):
        return analysis_offline.prepare_train_set(mgrs)
    def __repr__(self):
        return str({"CLASS": self.__class__.__name__})
    
class SVM(object):
    def __init__(self, C, Cmode , kernel, folds=5, ret='balancedSuccessRate'):
        self.C = C
        self.Cmode = Cmode
        self.kernel = kernel
        self.folds = folds
        self.ret = ret
    def process(self, train_data):
        return analysis_offline.svm(train_data, 
                                    self.C, self.Cmode, self.kernel, self.folds, self.ret)
    def __repr__(self):
        d = {"CLASS": self.__class__.__name__,
             "Cmode":self.Cmode,
             "folds":str(self.folds),
             "s.C":str(self.C)}
        k_class = self.kernel.__class__.__name__
        if k_class == 'Polynomial':
            k_class = k_class+"("+str(self.kernel.degree)+")"
        elif k_class == 'Gaussian':
            k_class = k_class+"("+str(self.kernel.gamma)+")"
        d['kernel'] = k_class
        return str(d)

class P300SVM(object):
    def __init__(self, C, Cmode, kernel):
        self.C = C
        self.Cmode = Cmode
        self.kernel = kernel
    def process(self, mgrs):
        return analysis_offline.p300_svm(mgrs,
                                    self.C, self.Cmode, self.kernel)
    def __repr__(self):
        return str({"CLASS": self.__class__.__name__,
                    "Cmode":self.Cmode,
                    "kernel": self.kernel.__class__.__name__,
                    "s.C":str(self.C)})

class Segment(object):
    def __init__(self, classes, start_offset, duration):
        self.classes = classes
        self.start_offset = start_offset
        self.duration = duration

    def process(self, mgrs):
        new_mgrs = []
        for mgr in mgrs:
            new_mgrs = new_mgrs + analysis_offline.segment(mgr, self.classes, self.start_offset, self.duration)
        return new_mgrs

    def __repr__(self):
        return str({"CLASS": self.__class__.__name__,
                    "classes": self.classes,
                    "start_offset": self.start_offset,
                    "duration": self.duration})


class Average(object):
    def __init__(self, bin_selectors, bin_names, size, baseline, strategy):
        self.bin_selectors = bin_selectors
        self.bin_names = bin_names
        self.size = size
        self.baseline = baseline
        self.strategy = strategy
    def process(self, mgrs):
        return analysis_offline.average(mgrs, self.bin_selectors, self.bin_names,
                                        self.size, self.baseline, self.strategy)
    def __repr__(self):
        return str({"CLASS": self.__class__.__name__,
                    "bin_selectors": str(self.bin_selectors),
                    "bin_names": self.bin_names,
                    "size": self.size,
                    "baseline": self.baseline,
                    "strategy": self.strategy
                    })


class Filter(object):
    def __init__(self, wp, ws, gpass, gstop, analog=0, ftype='ellip', output='ba', unit='radians'):
        self.wp = wp
        self.ws = ws
        self.gpass = gpass
        self.gstop = gstop
        self.analog = analog
        self.ftype = ftype
        self.output = output
        self.unit = unit
    def process(self, mgrs):
        new_mgrs = []
        for mgr in mgrs:
            new_mgrs.append(analysis_offline.filter(mgr, self.wp, self.ws, self.gpass, self.gstop, 
                                                    self.analog, self.ftype, self.output, self.unit))
        return new_mgrs
    def __repr__(self):
        ret = self.__dict__.copy()
        ret["CLASS"] = self.__class__.__name__
        return str(ret)



class Downsample(object):
    def __init__(self, factor):
        self.factor = factor
    def process(self, mgrs):
        new_mgrs = []
        for mgr in mgrs:
            new_mgrs.append(analysis_offline.downsample(mgr, self.factor))
        return new_mgrs
    def __repr__(self):
        ret = self.__dict__.copy()
        ret["CLASS"] = self.__class__.__name__
        return str(ret)



class ToMvTransform(object):
    def __init__(self):
        pass
    def process(self, p_mgrs):
        pass
        #dla każdego mgr-a:
        # pobierz jego gain i offset i zrób jego dane danymi w mikrowoltach


                
class Plot(object):
    def __init__(self, channel):
        self.channel = channel
    def process(self, mgrs):
        for mgr in mgrs:
            analysis_offline.plot(mgr, self.channel)
        return mgrs
    def __repr__(self):
        ret = {}
        ret["CLASS"] = self.__class__.__name__
        return str(ret)
