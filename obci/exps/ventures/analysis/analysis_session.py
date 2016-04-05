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
from obci.analysis.obci_signal_processing.tags.smart_tag_definition import SmartTagEndTagDefinition as STD
from obci.analysis.obci_signal_processing.smart_tags_manager import SmartTagsManager as STM
import analysis_helper
from matplotlib import pyplot as plt

SESSION_DATA_DIR = '~/ventures_experiment_data/'
SESSION_USERS = ['MC']#, 'SC', 'MC']


def display(data):
    f = plt.figure()
    ax1 = f.add_subplot(211)
    ax2 = f.add_subplot(212)
    step_len = 0
    for session_number in data.keys():
        times = []
        levels = []
        step_times = []
        levels_numbers = sorted([int(i) for i in data[session_number].keys()])
        for level_number in levels_numbers:
            for level in data[session_number][str(level_number)]:
                times.append(sum(level))
                levels.append(level_number)
                step_times.append(level)
        ax1.plot(levels, times, '--o')
        ax2.plot(range(step_len, len(sum(step_times, []))+ step_len), sum(step_times, []))
        lines = []
        i_=step_len
        for i in step_times:
            i_+=len(i)
            lines.append(i_)

        [ax2.vlines(i, 0, 50, alpha=0.5) for i in lines]
        #ax1.set_ylim(0, 180)
        #ax2.set_ylim(0, 180)
        step_len += len(sum(step_times, []))
    plt.show()
    pass

def get_session_times(file_name):
    file_name = '.'.join(file_name.split('.')[:-2])
    mgr = RM('{}.obci.xml'.format(file_name), '{}.obci.raw'.format(file_name), '{}.game.tag'.format(file_name))
    mgr = analysis_helper.set_first_timestamp(mgr)
    mgr.set_param('sampling_frequency', 60)
    session_number = int(mgr.get_tags()[0]['desc']['type'])
    smart_tag_definicion_level = STD(start_tag_name= 'level_start', end_tags_names='level_finish')
    levels_tags = STM(smart_tag_definicion_level, '', '', '', mgr).get_smart_tags()
    session_data = {}
    for level_tags in levels_tags:
        level_tags = level_tags.get_tags()
        level_data = []
        for tag in level_tags:
            if tag['name'] == 'level_start':
                t = float(tag['start_timestamp'])
            if tag['name'] == 'move':
                level_data.append(float(tag['start_timestamp'])-t)
                t = float(tag['start_timestamp'])
        try:
            session_data[level_tags[0]['desc']['type']].append(level_data)
        except:
            session_data[level_tags[0]['desc']['type']] = [level_data]

    return {session_number:session_data}

if __name__ == '__main__':
    #data_2_plot = {}
    for user_id in SESSION_USERS:
        name_search = '{}_ventures_game*.game.tag'.format(user_id)
        all_user_data = {}
        for file_name in analysis_helper.get_file_name(name_search, SESSION_DATA_DIR):
            user_data = get_session_times(file_name)
            all_user_data.update(user_data)
        display(all_user_data)
        break
            #data_2_plot.update(user_data)
    #display(data_2_plot)