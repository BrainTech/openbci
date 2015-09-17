#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#       Mateusz Biesaga <mateusz.biesaga@gmail.com>
# About script:
#       Creates csv, which contains p-values of Wilcoxon pair statistic, and
#   additionally information of direction of change (+ or -)

from __future__ import print_function, division
from os import *
from scipy.stats import wilcoxon
import pandas as pd

def get_group_data(marker, test, group):
    """
    :params: defined in main part of the script, indicate files with input
        data.
    :return: lists with values of marker in test for one group (one for
        pretest, one for posttest).
    """
    file_path = 'data/markers_' + marker + '.csv'
    data = pd.read_csv(file_path, index_col=0, dtype='str')

    test_pre = test + '_pre'
    test_post = test + '_post'
    pre_str = data[data['session_type'] == group][test_pre].values
    post_str = data[data['session_type'] == group][test_post].values

    pre = []
    post = []
    for elem in pre_str:
        if elem is not ' ':
            elem = float(elem)
            pre.append(elem)
    for elem in post_str:
        if elem is not ' ':
            elem = float(elem)
            post.append(elem)

    return pre, post

def average_difference_sign(pre, post):
    """
    Counts direction of change.
    """
    sum = 0
    for i in range(0, len(pre)):
        sum += post[i] - pre[i]
    if sum/len(pre) == 0:
        return 0
    elif sum/len(pre) < 0:
        return '-'
    else:
        return '+'


if __name__ == '__main__':

    # define here your input data
    markers = ['mean', 'mean_x', 'mean_y']
    tests = ['stanie', 'oczy', 'bacznosc', 'gabka', 'poznawcze']
    groups = ['cognitive', 'cognitive_motor', 'motor']

    # main part of the script
    analysis = pd.DataFrame()
    for marker in markers:
        for test in tests:
            if (marker == 'romberg' and test == 'stanie'):
                continue
            test_data = pd.DataFrame()
            test_data['marker'] = pd.Series(marker)
            test_data['test'] = pd.Series(test)
            for group in groups:
                pre, post = get_group_data(marker, test, group)
                test_data['{}_{}'.format('p_wilcoxon', group)] \
                    = pd.Series(wilcoxon(pre, post)[1])
                test_data['{}_{}'.format('sign', group)] \
                    = pd.Series(average_difference_sign(pre, post))

            analysis = analysis.append(test_data)

    analysis.to_csv("data/wilcoxon_next_markers.csv", sep=',')
