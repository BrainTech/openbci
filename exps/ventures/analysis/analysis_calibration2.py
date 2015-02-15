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

from obci.acquisition import acquisition_helper
from obci.analysis.obci_signal_processing.read_manager import ReadManager as RM
import analysis_helper
from matplotlib import pyplot as plt

CALIBRATION_2_DATA_DIR = '~/ventures_experiment_data/'
CALIBRATION_2_USERS = ['ML']#, 'ML', 'SC', 'MC']


def display(data):
    f = plt.figure()
    colors = ['r', 'b', 'y', 'g', 'm', 'c', 'k']
    for direction, ind_plot in zip(['up', 'left', 'right', 'down'], [2, 4, 6, 8]):
        f.add_subplot(3,3,ind_plot)
        plt.title(direction)
        print '*********************************'
        print direction
        for ind, user in enumerate(data.keys()):
            plt.plot(data[user][direction]['time'][0], data[user][direction]['level'][0], 'o'+colors[ind])
            plt.plot(data[user][direction]['time'][1], data[user][direction]['level'][1], '>'+colors[ind])
            print user, colors[ind]
        plt.xlim(0, 30)
        plt.ylim(0, 150)
    plt.show()

def get_calibration_2_times(file_name):
    file_name = '.'.join(file_name.split('.')[:-2])
    mgr = RM('{}.obci.xml'.format(file_name), '{}.obci.raw'.format(file_name), '{}.game.tag'.format(file_name))
    tags = mgr.get_tags()
    data = {'up':{'time':[[],[]], 'level': [[],[]]},
            'down': {'time':[[],[]], 'level': [[],[]]},
            'right': {'time':[[],[]], 'level': [[],[]]} ,
            'left': {'time':[[],[]], 'level': [[],[]]}}
    for i in range(0, len(tags),3):
        tags_= tags[i:i+3]
        if len(tags_) == 3:
            data[tags_[1]['desc']['type']]['time'][int(tags_[2]['desc']['type'])].append(float(tags_[2]['start_timestamp'])-float(tags_[0]['start_timestamp']))
            data[tags_[1]['desc']['type']]['level'][int(tags_[2]['desc']['type'])].append(int(tags_[0]['desc']['type']))
    return {file_name:data}


if __name__ == '__main__':
    data_2_plot = {}
    for user_id in CALIBRATION_2_USERS:
        name_search = '{}_ventures_calibration2*.game.tag'.format(user_id)
        for file_name in analysis_helper.get_file_name(name_search, CALIBRATION_2_DATA_DIR):
            print file_name
            user_data = get_calibration_2_times(file_name)
            data_2_plot.update(user_data)
    display(data_2_plot)
