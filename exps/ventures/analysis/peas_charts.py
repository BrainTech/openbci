from __future__ import print_function, division

from obci.analysis.balance.wii_read_manager import WBBReadManager
from obci.analysis.balance.wii_analysis import *
from obci.analysis.balance.raw_analysis import *
from obci.analysis.balance.wii_preprocessing import *

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

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
