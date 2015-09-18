from __future__ import print_function, division
from os import *

from obci.analysis.balance.wii_read_manager import WBBReadManager
from obci.analysis.balance.wii_analysis import *
from obci.analysis.balance.raw_analysis import *
from obci.analysis.balance.wii_preprocessing import *

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib import colors
from matplotlib.collections import LineCollection
from random import randint

def print_plots(x, y, task, user, param):
    x -= np.mean(x)
    y -= np.mean(y)
    r = np.sqrt(x*x + y*y)

    # fft = np.fft.fft(x)

    code = str(len(task)-2) + str(param) + str(unichr(randint(65, 90))) + user[5]

    t = np.linspace(0, 20, len(x))

    ax_xy = plt.subplot2grid((2, 2), (0, 1), rowspan=2)
    ax_xy.set_title(code)
    t_col = np.linspace(0, 10, 780)
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, cmap=plt.get_cmap('spectral'),
        norm=plt.Normalize(0, 10))
    lc.set_array(t_col)
    lc.set_linewidth(2)
    plt.gca().add_collection(lc)
    plt.xlim(-3, 3)
    plt.ylim(-3, 3)
    plt.xticks(np.arange(-3, 3, 0.2))
    plt.yticks(np.arange(-3, 3, 0.2))
    plt.tick_params(axis='both', labelsize=7)

    ax_x = plt.subplot2grid((2, 2), (0, 0))
    ax_x.set_ylabel('X')
    if task == 'ss':
        ax_x.set_title('stanie')
    else:
        ax_x.set_title(task[3:])
    points = np.array([t, x]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, cmap=plt.get_cmap('spectral'),
        norm=plt.Normalize(0, 10))
    lc.set_array(t_col)
    lc.set_linewidth(2)
    plt.gca().add_collection(lc)
    plt.xlim(0, 20)
    plt.ylim(-3, 3)
    plt.xticks(np.arange(0, 20, 1))
    plt.yticks(np.arange(-3, 3, 0.5))
    plt.tick_params(axis='both', labelsize=7)

    ax_y = plt.subplot2grid((2, 2), (1, 0))
    ax_y.set_ylabel('Y')
    points = np.array([t, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, cmap=plt.get_cmap('spectral'),
        norm=plt.Normalize(0, 10))
    lc.set_array(t_col)
    lc.set_linewidth(2)
    plt.gca().add_collection(lc)
    plt.xlim(0, 20)
    plt.ylim(-3, 3)
    plt.xticks(np.arange(0, 20, 1))
    plt.yticks(np.arange(-3, 3, 0.5))
    plt.tick_params(axis='both', labelsize=7)

    plt.tight_layout()
    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())
    plt.show()

class User(object):
    def __init__(self, user):
        self.username = user
        # print(user)
        self.session_type = users_data[users_data['ID']==self.username]['session_type'].values[0]
        self.alt_username = users_data[users_data['ID']==self.username]['alt_ID'].values[0]
        self.wbb_post = None
        self.wbb_pre = None
        for file in file_list:
            if self.username in file and 'pre' in file[10:]:
                # print(file)
                self.wbb_pre = get_read_manager(file)
            if self.username in file and 'post' in file[10:]:
                # print(file)
                self.wbb_post = get_read_manager(file)

        # for file in file_list_dual:
        #     if self.username in file and 'pre' in file:
        #         self.wbb_dual_pre = get_read_manager_dual(file)
        #     if self.username in file and 'post' in file:
        #         self.wbb_dual_post = get_read_manager_dual(file)
        # if user_task_checker(self.username, 'pre_post'):
        #     self.velo, self.mean_dist_x, self.mean_dist_y, self.mean_dist = \
        #         get_markers(self.wbb_pre, self.wbb_post, self.username, self.session_type, self.alt_username)
        # else:
        #     self.velo = None
        #     self.mean_dist = None
        #     self.mean_dist_x = None
        #     self.mean_dist_y = None
        # if user_task_checker(self.username, 'dual'):
        #     self.dual_dist, self.dual_dist_x, self.dual_dist_y = \
        #         get_dual_markers(self.wbb_dual_pre, self.wbb_dual_post, self.username, self.session_type)
        # else:
        #     self.dual_dist = None
        #     self.dual_dist_x = None
        #     self.dual_dist_y = None
        # self.dual_dist = average(self.dual_dist)
        # self.dual_dist_x = average(self.dual_dist_x)
        # self.dual_dist_y = average(self.dual_dist_y)

if __name__ == '__main__':
    users_data = pd.read_csv('./users.csv', index_col=0, dtype='str')
    users_names = users_data['ID'].values

    file_list = get_file_list('pre_post')
    file_list_dual = get_file_list('dual')

    users = []
    for user in users_names:
        user_object = User(user)
        users.append(user_object)

    users = set(users)
    users = list(users)

    # markers_velo = pd.DataFrame()
    # markers_mean_x = pd.DataFrame()
    # markers_mean_y = pd.DataFrame()
    # markers_mean = pd.DataFrame()
    # markers_dual_mean_x = pd.DataFrame()
    # markers_dual_mean_y = pd.DataFrame()
    # markers_dual_mean = pd.DataFrame()

    # for user in users:
    #     markers_velo = markers_velo.append(user.velo)
    #     markers_mean_x = markers_mean_x.append(user.mean_dist_x)
    #     markers_mean_y = markers_mean_y.append(user.mean_dist_y)
    #     markers_mean = markers_mean.append(user.mean_dist)
    #     markers_dual_mean_x = markers_dual_mean_x.append(user.dual_dist_x)
    #     markers_dual_mean_y = markers_dual_mean_y.append(user.dual_dist_y)
    #     markers_dual_mean = markers_dual_mean.append(user.dual_dist)
    #
    # markers_dual_mean = average(markers_dual_mean)
    # markers_dual_mean_x = average(markers_dual_mean_x)
    # markers_dual_mean_y = average(markers_dual_mean_y)
    #
    # markers_velo.to_csv("data/markers_velo.csv", sep=',')
    # markers_mean_x.to_csv("data/markers_mean_x.csv", sep=',')
    # markers_mean_y.to_csv("data/markers_mean_y.csv", sep=',')
    # markers_mean.to_csv("data/markers_mean.csv", sep=',')
    # markers_dual_mean_x.to_csv("data/markers_dual_mean_x.csv", sep=',')
    # markers_dual_mean_y.to_csv("data/markers_dual_mean_y.csv", sep=',')
    # markers_dual_mean.to_csv("data/markers_dual_mean.csv", sep=',')

    tasks = ['ss', 'ss_oczy', 'ss_bacznosc', 'ss_gabka', 'ss_poznawcze']
    fib = [1, 2, 3, 5, 8]

    for task in tasks:
        for user in users:
            if user.wbb_pre is not None and user.wbb_post is not None:
                param = randint(0, 9)
                if param in fib:
                    x, y = get_data_fragment(user.wbb_post, task+'_start', task+'_stop')
                    print_plots(x, y, task, user.alt_username, param)
                    x, y = get_data_fragment(user.wbb_pre, task+'_start', task+'_stop')
                    print_plots(x, y, task, user.alt_username, '0')
                else:
                    x, y = get_data_fragment(user.wbb_pre, task+'_start', task+'_stop')
                    print_plots(x, y, task, user.alt_username, param)
                    x, y = get_data_fragment(user.wbb_post, task+'_start', task+'_stop')
                    print_plots(x, y, task, user.alt_username, '3')


