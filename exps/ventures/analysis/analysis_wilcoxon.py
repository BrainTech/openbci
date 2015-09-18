#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#       Mateusz Biesaga <mateusz.biesaga@gmail.com>
#

from __future__ import print_function, division
from os import *
from scipy.stats import wilcoxon
import pandas as pd
import analysis_markers

if __name__ == '__main__':

    # define here your input data
    markers = ['mean', 'mean_x', 'mean_y']
    tests = ['stanie', 'oczy', 'bacznosc', 'gabka', 'poznawcze']
    groups = ['cognitive', 'cognitive_motor', 'motor']

    # main part of the script
    analysis = pd.DataFrame()
    for marker in markers:
        for test in tests:
            if marker == 'romberg' and test == 'stanie':
                continue
            test_data = pd.DataFrame()
            test_data['marker'] = pd.Series(marker)
            test_data['test'] = pd.Series(test)
            for group in groups:
                pre, post = analysis_markers.get_group_data(marker, test, group)
                test_data['{}_{}'.format('p_wilcoxon', group)] \
                    = pd.Series(wilcoxon(pre, post)[1])
                test_data['{}_{}'.format('sign', group)] \
                    = pd.Series(analysis_markers.average_difference_sign(pre, post))
            analysis = analysis.append(test_data)

    analysis.to_csv("data/wilcoxon_next_markers.csv", sep=',')
