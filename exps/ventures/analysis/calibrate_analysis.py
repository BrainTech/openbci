from __future__ import print_function, division
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import analysis_helper, analysis_user_file

DIRECTIONS = ['up', 'down', 'left', 'right']
SESSION_TYPES = ['cognitive_motor', 'motor']

class UserCalibrationData(object):
    def __init__(self, user):
        self.name = user
        self.number = int(data1[data1['ID']==self.name]['number'].values[0])
        self.session_type = analysis_user_file.get_session_type(self.name)
        self.calibration1_raw_data = self.get_calib_data()
        self.calibration1_data = self.transform_calib1_data()
        self.calibration2_data = self.get_calib_data(param=2)
        self.data_out = self.get_data_out()
        self.t = np.linspace(1, len(self.data_out['up']),
                                num=len(self.data_out['up']))
        self.fitted_lines = self.fit_lines()

    def get_calib_data(self, param=1):
        if param == 1:
            data = data1
        elif param == 2:
            data = data2
        else:
            print("Wrong parameter")
            return None
        calibration1_raw_data = {}
        for direction in DIRECTIONS:
            calibration_one_direction = []
            for column in range(1, self.number+1):
                calibration_one_direction.append(data[data['ID']==self.name][str(column)+'_'+direction].values[0])
            calibration1_raw_data[direction] = calibration_one_direction
        return calibration1_raw_data

    def transform_calib1_data(self):
        calibration1_data = {}
        for direction in DIRECTIONS:
            data_one_direction = []
            for elem in self.calibration1_raw_data[direction]:
                if direction == 'up' or direction == 'down':
                    new_elem = float(elem) * 13
                else:
                    new_elem = float(elem) * 22.5
                data_one_direction.append(new_elem)
            calibration1_data[direction] = data_one_direction
        return calibration1_data

    def get_data_out(self):
        data_out = {}
        for direction in DIRECTIONS:
            data_one_direction = []
            for elem1, elem2 in zip(self.calibration1_data[direction],
                                    self.calibration2_data[direction]):
                new_elem = elem1 * float(elem2)
                new_elem /= 100
                data_one_direction.append(new_elem)
            data_out[direction] = data_one_direction
        return data_out

    def fit_lines(self):
        fitted = {}
        for direction in DIRECTIONS:
            line = np.polyfit(self.t, self.data_out[direction], 1)
            fitted[direction] = line
        return fitted
if __name__ == "__main__":

    # read calibration data files
    data1 = pd.read_csv('../data/calibration_results_modified.csv',
                        index_col=0, dtype='str')
    data2 = pd.read_csv('../data/calibration_results_2_modified.csv',
                        index_col=0, dtype='str')

    # create UserCalibrationData objects
    user_list = analysis_helper.get_users(path='calibration_results_modified.csv')
    calibration_data_list = []
    for elem in user_list:
        if len(elem) == 4:
            calibration_data_list.append(UserCalibrationData(elem))

    # draw figures for each user
    for session_type in SESSION_TYPES:
        for user_data in calibration_data_list:
            if user_data.session_type == session_type:
                    # up
                plt.subplot2grid((3,4), (0,1), colspan=2)
                plt.plot(user_data.t, user_data.data_out['up'], 'o')
                plt.plot([1, user_data.t[-1]],
                         [user_data.fitted_lines['up'][0]+user_data.fitted_lines['up'][1],
                          user_data.fitted_lines['up'][0]*user_data.t[-1]+user_data.fitted_lines['up'][1]],
                         '--', color='r')
                plt.ylim(0, 14)
                plt.xlim(0.5, len(user_data.t)+0.5)
                plt.xticks(user_data.t)
                plt.title('up')
                plt.text(0.9, 0.8, 'a = '+str(user_data.fitted_lines['up'][0]))
                    # down
                plt.subplot2grid((3,4), (2,1), colspan=2)
                plt.plot(user_data.t, user_data.data_out['down'], 'o')
                plt.plot([1, user_data.t[-1]],
                     [user_data.fitted_lines['down'][0]+user_data.fitted_lines['down'][1],
                      user_data.fitted_lines['down'][0]*user_data.t[-1]+user_data.fitted_lines['down'][1]],
                     '--', color='r')
                plt.ylim(0, 14)
                plt.xlim(0.5, len(user_data.t)+0.5)
                plt.xticks(user_data.t)
                plt.title('down')
                plt.text(0.9, 0.8, 'a = '+str(user_data.fitted_lines['down'][0]))
                    # right
                plt.subplot2grid((3,4), (1,2), colspan=2)
                plt.plot(user_data.t, user_data.data_out['right'], 'o')
                plt.plot([1, user_data.t[-1]],
                     [user_data.fitted_lines['right'][0]+user_data.fitted_lines['right'][1],
                      user_data.fitted_lines['right'][0]*user_data.t[-1]+user_data.fitted_lines['right'][1]],
                     '--', color='r')
                plt.ylim(0, 23)
                plt.xlim(0.5, len(user_data.t)+0.5)
                plt.xticks(user_data.t)
                plt.title('right')
                plt.text(0.9, 0.8, 'a = '+str(user_data.fitted_lines['right'][0]))
                    # left
                plt.subplot2grid((3,4), (1,0), colspan=2)
                plt.plot(user_data.t, user_data.data_out['left'], 'o')
                plt.plot([1, user_data.t[-1]],
                     [user_data.fitted_lines['left'][0]+user_data.fitted_lines['left'][1],
                      user_data.fitted_lines['left'][0]*user_data.t[-1]+user_data.fitted_lines['left'][1]],
                     '--', color='r')
                plt.ylim(0, 23)
                plt.xlim(0.5, len(user_data.t)+0.5)
                plt.xticks(user_data.t)
                plt.title('left')
                plt.text(0.9, 0.8, 'a = '+str(user_data.fitted_lines['left'][0]))

                plt.suptitle(user_data.name+' '+user_data.session_type)
                mng = plt.get_current_fig_manager()
                mng.resize(*mng.window.maxsize())
                plt.show()

    # draw summary plot
