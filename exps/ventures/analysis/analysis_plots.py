#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#       Mateusz Biesaga <mateusz.biesaga@gmail.com>
#

from __future__ import print_function, division
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import pandas as pd
import numpy as np
import analysis_markers, analysis_user_file, analysis_helper

def draw_bar_chart(markers, groups, tests):
    """
    Prints bar chart showing comparison of pre- and post-values for
    each group (cognitive, cognitive-motor and motor).
    """
    for marker in markers:
        file_path = 'data/markers_' + marker + '.csv'
        data = pd.read_csv(file_path, index_col=0, dtype='str')

        for group in groups:
            stats = analysis_markers.basic_stats(data, group)

            N = len(tests)
            pre_means = []
            pre_devs = []
            post_means = []
            post_devs = []

            for test in tests:
                if marker == 'romberg' and test == 'stanie':
                    N -= 1
                    pass
                else:
                    pre_means.append(stats[stats['stat_name'] == 'mean'][test+'_pre'].values[0])
                    pre_devs.append(stats[stats['stat_name'] == 'std_dev'][test+'_pre'].values[0])
                    post_means.append(stats[stats['stat_name'] == 'mean'][test+'_post'].values[0])
                    post_devs.append(stats[stats['stat_name'] == 'std_dev'][test+'_post'].values[0])

            ind = np.arange(N)
            width = 0.35
            fig, ax = plt.subplots()
            rects1 = ax.bar(ind, pre_means, width, color='lightsage')
            rects2 = ax.bar(ind+width, post_means, width, color='lightseagreen')
            ax.set_ylabel('Means')
            ax.set_title('Mean values of Romberg stats - group: '+group)
            ax.set_xticks(ind+width)
            ax.set_xticklabels(tests)
            ax.legend((rects1[0], rects2[0]), ('PreTest', 'PostTest'),
                      bbox_to_anchor=(0.5, 1))
            plt.show()

def print_xy_plots(x, y, task, user, param):
    """
    Prints three plots: x(t), y(t) and y(x). Colors are used to enable
    the visibility of connection between time and the chart on the right.
    """
    x -= np.mean(x)
    y -= np.mean(y)

    t = np.linspace(0, 20, len(x))

    ax_xy = plt.subplot2grid((2, 2), (0, 1), rowspan=2)
    ax_xy.set_title(user+' '+task+'_'+param)
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


def xy_plots_manager(tasks, users):
    for task in tasks:
        for user in users:
            if user.wbb_pre is not None and user.wbb_post is not None:
                x, y = analysis_user_file.get_data_fragment(user.wbb_pre,
                                            task+'_start', task+'_stop')
                print_xy_plots(x, y, task, user.alt_username, 'pre')
                x, y = analysis_user_file.get_data_fragment(user.wbb_post,
                                            task+'_start', task+'_stop')
                print_xy_plots(x, y, task, user.alt_username, 'post')


def dual_plots(data_pre, data_post, user):
    """
    Saves plots showing ellipse area for the whole dual file.
    """
    plt.gcf().set_size_inches(12, 10)
    for i in range(3):
        if i == 0:
            titlee = 'stanie'
        elif i == 1:
            titlee = 'bacznosc'
        else:
            titlee = 'gabka'
        plt.subplot(3, 2, i*2+1)
        area = analysis_markers.count_area((58*i)+3, (58*i)+56, data_pre)
        plt.plot(area, 'o-')
        plt.ylim(0, 5)
        plt.xlim(0, 47)
        plt.axvspan(11, 23, color='red', alpha=0.3)
        plt.axvspan(35, 47, color='red', alpha=0.3)
        plt.title(titlee+'_pre')
        plt.subplot(3, 2, i*2+2)
        area = analysis_markers.count_area((58*i)+3, (58*i)+56, data_post)
        plt.plot(area, 'o-')
        plt.ylim(0, 5)
        plt.xlim(0, 47)
        plt.axvspan(11, 23, color='red', alpha=0.3)
        plt.axvspan(35, 47, color='red', alpha=0.3)
        plt.title(titlee+'_post')
    plt.suptitle(user + ' - ' + analysis_user_file.get_session_type(user))
    plt.savefig('./plots/'+user+'.png', dpi=120)
    plt.show()
    plt.close()

def proper(lista):
    new_list = []
    for elem in lista:
        try:
            new_list.append(float(elem))
        except ValueError:
            continue
        if str(elem) == 'nan':
            del new_list[-1]
    return new_list

class Point(object):
    def __init__(self, value_name, user):
        if 'poly' in value_name:
            self.y = data[data['username']==user][value_name].values[0]
            self.x = data[data['username']==user][value_name].index[0]
        else:
            self.y = data[data['username']==user][value_name+'_pre'].values[0]
            self.x = data[data['username']==user][value_name+'_post'].values[0]
        self.ses_type = data[data['username']==user]['session_type'].values[0]
        if self.ses_type == 'cognitive':
            self.color = 'b'
            self.shape = 'o'
        elif self.ses_type == 'cognitive_motor':
            self.color = 'g'
            self.shape = '^'
        elif self.ses_type == 'motor':
            self.color = 'r'
            self.shape = 'd'
        self.user = user
        try:
            self.y = float(self.y)
            self.x = float(self.x)
            self.active = True
        except ValueError:
            self.active = False
        if str(self.y) == 'nan' or str(self.x) == 'nan':
            self.active = False


if __name__ == '__main__':
    # bar charts:
    markers = ['romberg']
    groups = ['cognitive', 'cognitive_motor', 'motor']
    tests = ['stanie', 'oczy', 'bacznosc', 'gabka', 'poznawcze']
    draw_bar_chart(markers, groups, tests)

    # xy charts:
    users = analysis_helper.get_users_as_objects(analysis_helper.get_users())
    tasks = ['ss', 'ss_oczy', 'ss_bacznosc', 'ss_gabka', 'ss_poznawcze']
    xy_plots_manager(tasks, users)

    # dual ellipse plots:
    users = analysis_helper.get_complete_users()
    markers_path = pd.DataFrame()
    for user in users:
        print(user)
        w_pre, w_post = analysis_helper.get_read_managers_by_user(user)
        data_pre = analysis_user_file.get_short_data(w_pre)
        data_post = analysis_user_file.get_short_data(w_post)
        dual_plots(data_pre, data_post, user)

    # everything below - complex pre_post data plots:
    data = pd.read_csv('./data/i_love_huge_data.csv', index_col=0, dtype='str')
    users = data['username'].values

    ### STANIE ###
    mods = ['poly']
    markers = ['COP', 'elipsa', 'predkosc', 'odleglosc']
    i = 1

    for mod in mods:
        for marker in markers:
            points_filt = []

            for user in users:
                point = Point(mod+'_'+marker+'_ss_filt_xy', user)
                points_filt.append(point)

            mean_value_cog = []
            mean_value_cm = []
            mean_value_mot = []
            plt.subplot(2, 2, i)
            for point in points_filt:
                if point.active:
                    plt.plot(point.x, point.y, 'o', color=point.color, marker=point.shape)
                    if point.ses_type == 'cognitive':
                        mean_value_cog.append(point.y)
                    if point.ses_type == 'cognitive_motor':
                        mean_value_cm.append(point.y)
                    if point.ses_type == 'motor':
                        mean_value_mot.append(point.y)
            plt.title(mod+'_'+marker+'_ss_filt_xy', fontsize=10)
            plt.plot([0, 30], [np.mean(mean_value_cog), np.mean(mean_value_cog)], linestyle='--', color='b')
            plt.plot([0, 30], [np.mean(mean_value_cm), np.mean(mean_value_cm)], linestyle='--', color='g')
            plt.plot([0, 30], [np.mean(mean_value_mot), np.mean(mean_value_mot)], linestyle='--', color='r')
            i += 1

    plt.tight_layout()
    mng = plt.get_current_fig_manager()
    mng.resize(*mng.window.maxsize())
    plt.show()


    tasks = ['ss_oczy', 'ss_bacznosc', 'ss_poznawcze']

    mods = ['poly', 'romberg']
    markers = ['COP', 'elipsa', 'predkosc', 'odleglosc']


    for task in tasks:
        i = 1
        for mod in mods:
            for marker in markers:
                points_filt = []

                for user in users:
                    point = Point(mod+'_'+marker+'_'+task+'_filt_xy', user)
                    points_filt.append(point)

                if mod == 'poly':
                    mean_value_cog = []
                    mean_value_cm = []
                    mean_value_mot = []
                    plt.subplot(2, 4, i)
                    for point in points_filt:
                        if point.active:
                            plt.plot(point.x, point.y, 'o', color=point.color, marker=point.shape) #, label=point.user)
                            if point.ses_type == 'cognitive':
                                mean_value_cog.append(point.y)
                            if point.ses_type == 'cognitive_motor':
                                mean_value_cm.append(point.y)
                            if point.ses_type == 'motor':
                                mean_value_mot.append(point.y)
                    plt.title(mod+'_'+marker+'_'+task+'_filt_xy', fontsize=10)
                    # plt.legend()
                    # plt.show()
                    plt.plot([0, 30], [np.mean(mean_value_cog), np.mean(mean_value_cog)], linestyle='--', color='b')
                    plt.plot([0, 30], [np.mean(mean_value_cm), np.mean(mean_value_cm)], linestyle='--', color='g')
                    plt.plot([0, 30], [np.mean(mean_value_mot), np.mean(mean_value_mot)], linestyle='--', color='r')


                if mod == 'romberg':
                    plt.subplot(2, 4, i)
                    for point in points_filt:
                        try:
                            plt.plot(point.x, point.y, 'o', color=point.color, marker=point.shape)
                        except ValueError:
                            pass
                    plt.title(mod+'_'+marker+'_'+task+'_filt_xy', fontsize=10)

                    plt.plot([0, 30], [0, 30], linestyle='--')
                    plt.xlim(0, 2)
                    plt.ylim(0, 2)
                i += 1

        # plt.tight_layout()
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        plt.show()

    # ### POLY ###
    # mod = 'poly'
    # tasks = ['ss', 'ss_oczy', 'ss_bacznosc', 'ss_gabka', 'ss_poznawcze']
    # filt_axis = ['nonfilt_xy', 'filt_xy']
    #
    # markers = ['COP', 'elipsa']
    # for marker in markers:
    #     for task in tasks:
    #
    #         points_nonfilt = []
    #         points_filt = []
    #
    #         min_size = -75
    #         max_size = 75
    #
    #         for user in users:
    #             point = Point(mod+'_'+marker+'_'+task+'_nonfilt_xy', user)
    #             points_nonfilt.append(point)
    #             point = Point(mod+'_'+marker+'_'+task+'_filt_xy', user)
    #             points_filt.append(point)
    #
    #         plt.subplot(1, 2, 1)
    #         mean_value_cog = []
    #         mean_value_cm = []
    #         mean_value_mot = []
    #         for point in points_nonfilt:
    #             if point.active:
    #                 plt.plot(point.x, point.y, 'o', color=point.color, marker=point.shape)
    #                 if point.ses_type == 'cognitive':
    #                     mean_value_cog.append(point.y)
    #                 if point.ses_type == 'cognitive_motor':
    #                     mean_value_cm.append(point.y)
    #                 if point.ses_type == 'motor':
    #                     mean_value_mot.append(point.y)
    #         plt.plot([0, 30], [np.mean(mean_value_cog), np.mean(mean_value_cog)], linestyle='--', color='b')
    #         plt.plot([0, 30], [np.mean(mean_value_cm), np.mean(mean_value_cm)], linestyle='--', color='g')
    #         plt.plot([0, 30], [np.mean(mean_value_mot), np.mean(mean_value_mot)], linestyle='--', color='r')
    #         plt.title(mod+'_'+marker+'_'+task+'_nonfilt_xy')
    #         plt.ylim(min_size, max_size)
    #
    #         plt.subplot(1, 2, 2)
    #         mean_value_cog = []
    #         mean_value_cm = []
    #         mean_value_mot = []
    #         for point in points_filt:
    #             if point.active:
    #                 plt.plot(point.x, point.y, 'o', color=point.color, marker=point.shape)
    #                 if point.ses_type == 'cognitive':
    #                     mean_value_cog.append(point.y)
    #                 if point.ses_type == 'cognitive_motor':
    #                     mean_value_cm.append(point.y)
    #                 if point.ses_type == 'motor':
    #                     mean_value_mot.append(point.y)
    #         plt.plot([0, 30], [np.mean(mean_value_cog), np.mean(mean_value_cog)], linestyle='--', color='b')
    #         plt.plot([0, 30], [np.mean(mean_value_cm), np.mean(mean_value_cm)], linestyle='--', color='g')
    #         plt.plot([0, 30], [np.mean(mean_value_mot), np.mean(mean_value_mot)], linestyle='--', color='r')
    #         plt.title(mod+'_'+marker+'_'+task+'_filt_xy')
    #         plt.ylim(min_size, max_size)
    #
    #         plt.tight_layout()
    #         mng = plt.get_current_fig_manager()
    #         mng.resize(*mng.window.maxsize())
    #         plt.show()
    #
    # markers = ['predkosc', 'odleglosc']
    # for marker in markers:
    #     for task in tasks:
    #
    #         points_nonfilt_xy = []
    #         points_filt_xy = []
    #         points_nonfilt_x = []
    #         points_filt_x = []
    #         points_nonfilt_y = []
    #         points_filt_y = []
    #
    #         min_size = -75
    #         max_size = 75
    #
    #         for user in users:
    #             point = Point(mod+'_'+marker+'_'+task+'_nonfilt_xy', user)
    #             points_nonfilt_xy.append(point)
    #             point = Point(mod+'_'+marker+'_'+task+'_filt_xy', user)
    #             points_filt_xy.append(point)
    #             point = Point(mod+'_'+marker+'_'+task+'_nonfilt_x', user)
    #             points_nonfilt_x.append(point)
    #             point = Point(mod+'_'+marker+'_'+task+'_filt_x', user)
    #             points_filt_x.append(point)
    #             point = Point(mod+'_'+marker+'_'+task+'_nonfilt_y', user)
    #             points_nonfilt_y.append(point)
    #             point = Point(mod+'_'+marker+'_'+task+'_filt_y', user)
    #             points_filt_y.append(point)
    #
    #         plt.subplot(2, 3, 1)
    #         mean_value_cog = []
    #         mean_value_cm = []
    #         mean_value_mot = []
    #         for point in points_nonfilt_xy:
    #             if point.active:
    #                 plt.plot(point.x, point.y, 'o', color=point.color, marker=point.shape)
    #                 if point.ses_type == 'cognitive':
    #                     mean_value_cog.append(point.y)
    #                 if point.ses_type == 'cognitive_motor':
    #                     mean_value_cm.append(point.y)
    #                 if point.ses_type == 'motor':
    #                     mean_value_mot.append(point.y)
    #         plt.plot([0, 30], [np.mean(mean_value_cog), np.mean(mean_value_cog)], linestyle='--', color='b')
    #         plt.plot([0, 30], [np.mean(mean_value_cm), np.mean(mean_value_cm)], linestyle='--', color='g')
    #         plt.plot([0, 30], [np.mean(mean_value_mot), np.mean(mean_value_mot)], linestyle='--', color='r')
    #         plt.title(mod+'_'+marker+'_'+task+'_nonfilt_xy')
    #         plt.ylim(min_size, max_size)
    #
    #         plt.subplot(2, 3, 2)
    #         mean_value_cog = []
    #         mean_value_cm = []
    #         mean_value_mot = []
    #         for point in points_nonfilt_x:
    #             if point.active:
    #                 plt.plot(point.x, point.y, 'o', color=point.color, marker=point.shape)
    #                 if point.ses_type == 'cognitive':
    #                     mean_value_cog.append(point.y)
    #                 if point.ses_type == 'cognitive_motor':
    #                     mean_value_cm.append(point.y)
    #                 if point.ses_type == 'motor':
    #                     mean_value_mot.append(point.y)
    #         plt.plot([0, 30], [np.mean(mean_value_cog), np.mean(mean_value_cog)], linestyle='--', color='b')
    #         plt.plot([0, 30], [np.mean(mean_value_cm), np.mean(mean_value_cm)], linestyle='--', color='g')
    #         plt.plot([0, 30], [np.mean(mean_value_mot), np.mean(mean_value_mot)], linestyle='--', color='r')
    #         plt.title(mod+'_'+marker+'_'+task+'_nonfilt_x')
    #         plt.ylim(min_size, max_size)
    #
    #         plt.subplot(2, 3, 3)
    #         mean_value_cog = []
    #         mean_value_cm = []
    #         mean_value_mot = []
    #         for point in points_nonfilt_y:
    #             if point.active:
    #                 plt.plot(point.x, point.y, 'o', color=point.color, marker=point.shape)
    #                 if point.ses_type == 'cognitive':
    #                     mean_value_cog.append(point.y)
    #                 if point.ses_type == 'cognitive_motor':
    #                     mean_value_cm.append(point.y)
    #                 if point.ses_type == 'motor':
    #                     mean_value_mot.append(point.y)
    #         plt.plot([0, 30], [np.mean(mean_value_cog), np.mean(mean_value_cog)], linestyle='--', color='b')
    #         plt.plot([0, 30], [np.mean(mean_value_cm), np.mean(mean_value_cm)], linestyle='--', color='g')
    #         plt.plot([0, 30], [np.mean(mean_value_mot), np.mean(mean_value_mot)], linestyle='--', color='r')
    #         plt.title(mod+'_'+marker+'_'+task+'_nonfilt_y')
    #         plt.ylim(min_size, max_size)
    #
    #         plt.subplot(2, 3, 4)
    #         mean_value_cog = []
    #         mean_value_cm = []
    #         mean_value_mot = []
    #         for point in points_filt_xy:
    #             if point.active:
    #                 plt.plot(point.x, point.y, 'o', color=point.color, marker=point.shape)
    #                 if point.ses_type == 'cognitive':
    #                     mean_value_cog.append(point.y)
    #                 if point.ses_type == 'cognitive_motor':
    #                     mean_value_cm.append(point.y)
    #                 if point.ses_type == 'motor':
    #                     mean_value_mot.append(point.y)
    #         plt.plot([0, 30], [np.mean(mean_value_cog), np.mean(mean_value_cog)], linestyle='--', color='b')
    #         plt.plot([0, 30], [np.mean(mean_value_cm), np.mean(mean_value_cm)], linestyle='--', color='g')
    #         plt.plot([0, 30], [np.mean(mean_value_mot), np.mean(mean_value_mot)], linestyle='--', color='r')
    #         plt.title(mod+'_'+marker+'_'+task+'_filt_xy')
    #         plt.ylim(min_size, max_size)
    #
    #         plt.subplot(2, 3, 5)
    #         mean_value_cog = []
    #         mean_value_cm = []
    #         mean_value_mot = []
    #         for point in points_filt_x:
    #             if point.active:
    #                 plt.plot(point.x, point.y, 'o', color=point.color, marker=point.shape)
    #                 if point.ses_type == 'cognitive':
    #                     mean_value_cog.append(point.y)
    #                 if point.ses_type == 'cognitive_motor':
    #                     mean_value_cm.append(point.y)
    #                 if point.ses_type == 'motor':
    #                     mean_value_mot.append(point.y)
    #         plt.plot([0, 30], [np.mean(mean_value_cog), np.mean(mean_value_cog)], linestyle='--', color='b')
    #         plt.plot([0, 30], [np.mean(mean_value_cm), np.mean(mean_value_cm)], linestyle='--', color='g')
    #         plt.plot([0, 30], [np.mean(mean_value_mot), np.mean(mean_value_mot)], linestyle='--', color='r')
    #         plt.title(mod+'_'+marker+'_'+task+'_filt_x')
    #         plt.ylim(min_size, max_size)
    #
    #         plt.subplot(2, 3, 6)
    #         mean_value_cog = []
    #         mean_value_cm = []
    #         mean_value_mot = []
    #         for point in points_filt_y:
    #             if point.active:
    #                 plt.plot(point.x, point.y, 'o', color=point.color, marker=point.shape)
    #                 if point.ses_type == 'cognitive':
    #                     mean_value_cog.append(point.y)
    #                 if point.ses_type == 'cognitive_motor':
    #                     mean_value_cm.append(point.y)
    #                 if point.ses_type == 'motor':
    #                     mean_value_mot.append(point.y)
    #         plt.plot([0, 30], [np.mean(mean_value_cog), np.mean(mean_value_cog)], linestyle='--', color='b')
    #         plt.plot([0, 30], [np.mean(mean_value_cm), np.mean(mean_value_cm)], linestyle='--', color='g')
    #         plt.plot([0, 30], [np.mean(mean_value_mot), np.mean(mean_value_mot)], linestyle='--', color='r')
    #         plt.title(mod+'_'+marker+'_'+task+'_filt_y')
    #         plt.ylim(min_size, max_size)
    #
    #         mng = plt.get_current_fig_manager()
    #         mng.resize(*mng.window.maxsize())
    #         plt.show()