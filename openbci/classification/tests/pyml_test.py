#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""
This script show how to use PyML module.
"""
from PyML import *

def run():
    data = VectorDataSet('iris.data', labelsColumn = -1)
    #labels = data.labels.L
    #some_pattern = data.getPattern(2)
    #data.normalize()
    #number_of_features = data.numFeatures
    #number_of_trials = len(data)
    #number_of_every_class = labels.classSize
    data2 = data.__class__(data, classes = ['Iris-versicolor', 'Iris-virginica'])
    s = SVM()
    r = s.cv(data2)
    r.plotROC()


    param = modelSelection.Param(svm.SVM(), 'C', [0.1, 1, 10, 100, 1000])
    m = modelSelection.ModelSelector(param, measure='balancedSuccessRate')
    m.train(data2)
    #best_svm = m.classifier
    #best_svm_result = best_svm.cv(data2)
    

    


if __name__ == '__main__':
    run()
