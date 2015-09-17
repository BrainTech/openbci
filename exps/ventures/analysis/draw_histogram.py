#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#       Mateusz Biesaga <mateusz.biesaga@gmail.com>
# About script:
#       Prints simple bar charts on the basis of markers value.

from __future__ import print_function, division
import pandas as pd
from matplotlib import pyplot as plt
import numpy
import analysis_markers

if __name__ == '__main__':

    # define parameters here:
    marker = 'romberg'
    groups = ['cognitive', 'cognitive_motor', 'motor']

    for group in groups:

        file_path = 'data/markers_' + marker + '.csv'
        data = pd.read_csv(file_path, index_col=0, dtype='str')
        stats = analysis_markers.basic_stats(data, group)

        if marker == 'romberg':
            tests = ['oczy', 'bacznosc', 'gabka', 'poznawcze']
        else:
            tests = ['stanie', 'oczy', 'bacznosc', 'gabka', 'poznawcze']
        N = len(tests)

        pre_means = []
        pre_devs = []
        post_means = []
        post_devs = []

        for test in tests:
            pre_means.append(stats[stats['stat_name'] == 'mean'][test+'_pre'].values[0])
            pre_devs.append(stats[stats['stat_name'] == 'std_dev'][test+'_pre'].values[0])
            post_means.append(stats[stats['stat_name'] == 'mean'][test+'_post'].values[0])
            post_devs.append(stats[stats['stat_name'] == 'std_dev'][test+'_post'].values[0])

        ind = numpy.arange(N)
        width = 0.35

        fig, ax = plt.subplots()
        rects1 = ax.bar(ind, pre_means, width, color='lightsage')
        rects2 = ax.bar(ind+width, post_means, width, color='lightseagreen')

        ax.set_ylabel('Means')
        ax.set_title('Mean values of Romberg stats - group: '+group)
        ax.set_xticks(ind+width)
        ax.set_xticklabels(tests)

        ax.legend((rects1[0], rects2[0]), ('PreTest', 'PostTest'), bbox_to_anchor=(0.5, 1))

        plt.show()
