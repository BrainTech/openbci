# -*- coding: utf-8 -*-
#!/usr/bin/env python
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
#     Anna Chabuda <anna.chabuda@gmail.com>
#

import matplotlib.pyplot as plt 
import numpy as np

def display_signal(signal, channels_names_to_display, all_channels_names, title):
    fig = plt.figure()
    fig.suptitle(title)
    subplot_ind = 1
    for ind, ch_samples in enumerate(signal, 0):
        if all_channels_names[ind] in channels_names_to_display:
            ax = fig.add_subplot(len(channels_names_to_display), 1, subplot_ind)
            ax.plot(ch_samples)
            ax.set_title('{}'.format(channels_names_to_display[subplot_ind-1]))
            subplot_ind+=1

    plt.show()

def display_patterns(labels, data_to_display):
    fig = plt.figure()
    fig.suptitle("patterns")
    max_value = np.max(data_to_display)
    min_value = np.min(data_to_display)
    for ind, p_samples in enumerate(data_to_display, 1):
        ax = fig.add_subplot(len(labels), 1, ind)
        ax.plot(p_samples)
        ax.set_title('{}'.format(labels[ind-1]))
        ax.set_ylim(max_value, min_value)

    plt.show()


def display_auc(AUC):
    f = plt.figure()
    ax = f.add_subplot(111)
    for freq in AUC.keys():
        ax.plot(int(freq), AUC[freq], 'o')
    ax.legend(loc = 4)
    ax.set_xlim(29.5, 42)
    ax.set_xticks(range(30,42))
    ax.set_ylim(0, 1.1)
    plt.show()


def display_roc(ROC):
    f = plt.figure()
    ax1 = f.add_subplot(121)
    ax2 = f.add_subplot(122)
    color = ['r', 'b', 'g', 'm', 'c', 'y']
    c1 = 0
    c2 = 0
    for ind, freq in enumerate(ROC.keys()):
        if ind%2:
            ax1.plot(ROC[freq][0], ROC[freq][1], '--o'+color[c1], label=freq) 
            c1+=1
        else:
            ax2.plot(ROC[freq][0], ROC[freq][1], '--o'+color[c2], label=freq) 
            c2+=1
    ax1.set_xlim(-0.1, 1)
    ax1.set_ylim(0, 1.1)
    ax1.set_xlabel('1-SPC')
    ax1.set_ylabel('TPR')
    ax2.set_xlim(-0.1, 1)
    ax2.set_ylim(0, 1.1)
    ax2.set_xlabel('1-SPC')
    ax2.set_ylabel('TPR')
    ax1.legend(loc=4)
    ax2.legend(loc=4)
    plt.show()

def display_results(results,auc):
    print results
    f = plt.figure()
    ax1 = f.add_subplot(121)
    ax2 = f.add_subplot(122)
    color = ['r', 'b', 'g', 'm']
    c1 = 0
    c2 = 0
    target = []
    nontarget = []
    for ind, freq in enumerate(results.keys()):
        if ind%2:
            ax1.plot(range(0,8), results[freq][0], '--o'+color[c1], label='{} {}'.format(freq, auc[freq]))
            [ax1.plot(range(0,8), results[freq][i], '--o'+color[c1]) for i in range(1, len(results[freq]))] 
            c1+=1
            target.append([results[freq][i][5] for i in xrange(len(results[freq]))])
            nontarget.append(sum([[results[freq][j][i] for i in [0,1,2,3,4,6,7]] for j in xrange(len(results[freq]))], []))
        else:
            ax2.plot(range(0,8), results[freq][0], '--o'+color[c2], label='{} {}'.format(freq, auc[freq]))
            [ax2.plot(range(0,8), results[freq][i], '--o'+color[c2]) for i in range(1, len(results[freq]))]
            
            target.append([results[freq][i][5] for i in xrange(len(results[freq]))])
            nontarget.append(sum([[results[freq][j][i] for i in [0,1,2,3,4,6,7]] for j in xrange(len(results[freq]))], []))
            c2+=1
    ax1.legend(loc=2)
    ax2.legend(loc=2)
    nontarget = sum(nontarget, [])
    target = sum(target, [])
    print len(target), len(nontarget), len(nontarget)/len(target)
    plt.show()
    plt.figure()
    plt.hist(target)
    plt.hist(nontarget)
    plt.show()


