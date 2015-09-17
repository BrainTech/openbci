from __future__ import print_function, division
from os import *

from matplotlib import pyplot as plt
import pandas as pd

from obci.analysis.balance.wii_read_manager import WBBReadManager
from obci.analysis.balance.wii_analysis import *
from obci.analysis.balance.wii_preprocessing import *
from obci.analysis.obci_signal_processing.tags import tags_file_writer as tags_writer
from obci.analysis.obci_signal_processing.tags import tag_utils

def get_complete_users():
    names_list = []
    for paths, subcatalogs, files in walk(r'./dual_data/'):
        for subcatalog in subcatalogs:
            if subcatalog not in names_list and len(subcatalog) == 4 and subcatalog[3].isdigit():
                names_list.append(subcatalog)
    return names_list

def file_by_extension(file_list, extention):
    for file in file_list:
        if file[-(len(extention)):] == extention:
            return file
    return None

def wii_preprocessing_signal(file_list, after_tag_change=True):
    if after_tag_change:
        w = WBBReadManager(file_by_extension(file_list, 'led.obci.xml'),
                       file_by_extension(file_list, 'led.obci.raw'),
                       file_by_extension(file_list, 'tag.tag'))
    else:
        w = WBBReadManager(file_by_extension(file_list, 'led.obci.xml'),
                       file_by_extension(file_list, 'led.obci.raw'),
                       file_by_extension(file_list, '.psychopy.tag'))

    w = wii_filter_signal(w, 33.5/2, 2, use_filtfilt=True)
    return w

def get_mgrs(user, after_tag_change=True):
    path_list = []
    for paths, subcats, files in walk('./dual_data/' + user + '/pre'):
        for file in files:
            path_to_file = './dual_data/' + user + '/pre/' + file
            path_list.append(path_to_file)
    w_pre = wii_preprocessing_signal(path_list, after_tag_change)
    path_list = []
    for paths, subcats, files in walk('./dual_data/' + user + '/post'):
        for file in files:
            path_to_file = './dual_data/' + user + '/post/' + file
            path_list.append(path_to_file)
    w_post = wii_preprocessing_signal(path_list, after_tag_change)
    return w_pre, w_post

def get_session_type(name):
    data = pd.read_csv('./data/users.csv', index_col=0, dtype='str')
    if name in data['ID'].values:
        return data[data['ID']==name]['session_type'].values[0]
    else:
        return None

def adjust_timestamp(w, user, prefix):
    ts1 = w.mgr.get_param('first_sample_timestamp')
    ts2 = w.mgr.get_tags()[0]['desc']['value']
    delay = float(ts2) - float(ts1)

    writer = tags_writer.TagsFileWriter('./dual_data/' + user + '/' + prefix + '/adjusted_tag.tag')
    help_variable = 1
    for i in range(1, len(w.mgr.get_tags())):
        if w.mgr.get_tags()[i]['name'] == 'ss_start':
            task = ''
        if w.mgr.get_tags()[i]['name'] == 'ss_bacznosc_start':
            task = 'bacznosc_'
        if w.mgr.get_tags()[i]['name'] == 'ss_gabka_start':
            task = 'gabka_'
        if w.mgr.get_tags()[i-1]['desc'] == {} and w.mgr.get_tags()[i]['name'] == 'zgodny':
            tag = tag_utils.pack_tag_to_dict(w.mgr.get_tags()[i]['start_timestamp'] + delay,
                                         w.mgr.get_tags()[i]['end_timestamp'] + delay,
                                         'ss_' + task + 'zgodny1_start',
                                         {})
            writer.tag_received(tag)
        if w.mgr.get_tags()[i-1]['name'] == 'zgodny' and w.mgr.get_tags()[i]['name'] == 'niezgodny':
            tag = tag_utils.pack_tag_to_dict(w.mgr.get_tags()[i]['start_timestamp'] + delay,
                                         w.mgr.get_tags()[i]['end_timestamp'] + delay,
                                         'ss_' + task + 'zgodny' + str(help_variable) + '_stop',
                                         {})
            writer.tag_received(tag)
            tag = tag_utils.pack_tag_to_dict(w.mgr.get_tags()[i]['start_timestamp'] + delay,
                                         w.mgr.get_tags()[i]['end_timestamp'] + delay,
                                         'ss_' + task + 'niezgodny' + str(help_variable) + '_start',
                                         {})
            writer.tag_received(tag)
            help_variable = 2
        if w.mgr.get_tags()[i-1]['name'] == 'niezgodny' and w.mgr.get_tags()[i]['name'] == 'zgodny':
            tag = tag_utils.pack_tag_to_dict(w.mgr.get_tags()[i]['start_timestamp'] + delay,
                                         w.mgr.get_tags()[i]['end_timestamp'] + delay,
                                         'ss_' + task + 'niezgodny1_stop',
                                         {})
            writer.tag_received(tag)
            tag = tag_utils.pack_tag_to_dict(w.mgr.get_tags()[i]['start_timestamp'] + delay,
                                         w.mgr.get_tags()[i]['end_timestamp'] + delay,
                                         'ss_' + task + 'zgodny2_start',
                                         {})
            writer.tag_received(tag)
        if w.mgr.get_tags()[i-1]['name'] == 'niezgodny' and w.mgr.get_tags()[i]['desc'] == {}:
            tag = tag_utils.pack_tag_to_dict(w.mgr.get_tags()[i]['start_timestamp'] + delay,
                                         w.mgr.get_tags()[i]['end_timestamp'] + delay,
                                         'ss_' + task + 'niezgodny2_stop',
                                         {})
            writer.tag_received(tag)
            help_variable = 1
        if i in [1, 50, 51, 100, 101, 150]:
            tag = tag_utils.pack_tag_to_dict(w.mgr.get_tags()[i]['start_timestamp'] + delay,
                                         w.mgr.get_tags()[i]['end_timestamp'] + delay,
                                         w.mgr.get_tags()[i]['name'],
                                         {})
            writer.tag_received(tag)
        else:
            tag = tag_utils.pack_tag_to_dict(w.mgr.get_tags()[i]['start_timestamp'] + delay,
                                         w.mgr.get_tags()[i]['end_timestamp'] + delay,
                                         w.mgr.get_tags()[i]['name'],
                                         {'znaczenie': w.mgr.get_tags()[i]['desc']['znaczenie'],
                                          'czcionka': w.mgr.get_tags()[i]['desc']['czcionka']})
            writer.tag_received(tag)
    writer.finish_saving(0.0)

def get_data(wbb_mgr):
    task_stanie_zgodny1 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_zgodny1_start',
                                    end_tags_names=['ss_zgodny1_stop'], TS=True)
    task_stanie_zgodny2 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_zgodny2_start',
                                    end_tags_names=['ss_zgodny2_stop'], TS=True)
    task_stanie_niezgodny1 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_niezgodny1_start',
                                    end_tags_names=['ss_niezgodny1_stop'], TS=True)
    task_stanie_niezgodny2 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_niezgodny2_start',
                                    end_tags_names=['ss_niezgodny2_stop'], TS=True)

    task_bacznosc_zgodny1 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_bacznosc_zgodny1_start',
                                    end_tags_names=['ss_bacznosc_zgodny1_stop'], TS=True)
    task_bacznosc_zgodny2 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_bacznosc_zgodny2_start',
                                    end_tags_names=['ss_bacznosc_zgodny2_stop'], TS=True)
    task_bacznosc_niezgodny1 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_bacznosc_niezgodny1_start',
                                    end_tags_names=['ss_bacznosc_niezgodny1_stop'], TS=True)
    task_bacznosc_niezgodny2 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_bacznosc_niezgodny2_start',
                                    end_tags_names=['ss_bacznosc_niezgodny2_stop'], TS=True)

    task_gabka_zgodny1 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_gabka_zgodny1_start',
                                    end_tags_names=['ss_gabka_zgodny1_stop'], TS=True)
    task_gabka_zgodny2 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_gabka_zgodny2_start',
                                    end_tags_names=['ss_gabka_zgodny2_stop'], TS=True)
    task_gabka_niezgodny1 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_gabka_niezgodny1_start',
                                    end_tags_names=['ss_gabka_niezgodny1_stop'], TS=True)
    task_gabka_niezgodny2 = wii_cut_fragments(wbb_mgr,
                                    start_tag_name='ss_gabka_niezgodny2_start',
                                    end_tags_names=['ss_gabka_niezgodny2_stop'], TS=True)

    return task_stanie_zgodny1, task_stanie_zgodny2, task_stanie_niezgodny1, task_stanie_niezgodny2, \
           task_bacznosc_zgodny1, task_bacznosc_zgodny2, task_bacznosc_niezgodny1, task_bacznosc_niezgodny2, \
           task_gabka_zgodny1, task_gabka_zgodny2, task_gabka_niezgodny1, task_gabka_niezgodny2

def get_markers(wbb_mgr_pre, wbb_mgr_post, username, sessiontype):
    user_data = pd.DataFrame()
    task_stanie_zgodny1_pre, task_stanie_zgodny2_pre, task_stanie_niezgodny1_pre, task_stanie_niezgodny2_pre, \
           task_bacznosc_zgodny1_pre, task_bacznosc_zgodny2_pre, task_bacznosc_niezgodny1_pre, task_bacznosc_niezgodny2_pre, \
           task_gabka_zgodny1_pre, task_gabka_zgodny2_pre, task_gabka_niezgodny1_pre, task_gabka_niezgodny2_pre = get_data(wbb_mgr_pre)
    task_stanie_zgodny1_post, task_stanie_zgodny2_post, task_stanie_niezgodny1_post, task_stanie_niezgodny2_post, \
           task_bacznosc_zgodny1_post, task_bacznosc_zgodny2_post, task_bacznosc_niezgodny1_post, task_bacznosc_niezgodny2_post, \
           task_gabka_zgodny1_post, task_gabka_zgodny2_post, task_gabka_niezgodny1_post, task_gabka_niezgodny2_post = get_data(wbb_mgr_post)
    for name, t in zip(['username', 'session_type'], [username, sessiontype]):
        user_data[name] = pd.Series([t])
    for name, t in zip(['stanie_zgodny1', 'stanie_zgodny2', 'stanie_niezgodny1', 'stanie_niezgodny2',
                        'bacznosc_zgodny1', 'bacznosc_zgodny2', 'bacznosc_niezgodny1', 'bacznosc_niezgodny2',
                        'gabka_zgodny1', 'gabka_zgodny2', 'gabka_niezgodny1', 'gabka_niezgodny2'],
                       [task_stanie_zgodny1_pre, task_stanie_zgodny2_pre, task_stanie_niezgodny1_pre, task_stanie_niezgodny2_pre,
                        task_bacznosc_zgodny1_pre, task_bacznosc_zgodny2_pre, task_bacznosc_niezgodny1_pre, task_bacznosc_niezgodny2_pre,
                        task_gabka_zgodny1_pre, task_gabka_zgodny2_pre, task_gabka_niezgodny1_pre, task_gabka_niezgodny2_pre]):

        x, y = remove_baseline(t)

        if len(x) < 300:
            user_data['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])
        else:
            user_data['{}_{}'.format(name, 'pre')] \
                = pd.Series([wii_COP_path(wbb_mgr_pre, x, y, plot=False)[0]])


    for name, t in zip(['stanie_zgodny1', 'stanie_zgodny2', 'stanie_niezgodny1', 'stanie_niezgodny2',
                        'bacznosc_zgodny1', 'bacznosc_zgodny2', 'bacznosc_niezgodny1', 'bacznosc_niezgodny2',
                        'gabka_zgodny1', 'gabka_zgodny2', 'gabka_niezgodny1', 'gabka_niezgodny2'],
                       [task_stanie_zgodny1_post, task_stanie_zgodny2_post, task_stanie_niezgodny1_post, task_stanie_niezgodny2_post,
                        task_bacznosc_zgodny1_post, task_bacznosc_zgodny2_post, task_bacznosc_niezgodny1_post, task_bacznosc_niezgodny2_post,
                        task_gabka_zgodny1_post, task_gabka_zgodny2_post, task_gabka_niezgodny1_post, task_gabka_niezgodny2_post]):

        x, y = remove_baseline(t)

        if len(x) < 300 or user_data[user_data['username']==username][name+'_pre'].values[0] == ' ':
            user_data['{}_{}'.format(name, 'post')] \
                = pd.Series([' '])
            user_data['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])
        else:
            user_data['{}_{}'.format(name, 'post')] \
                = pd.Series([wii_COP_path(wbb_mgr_post, x, y, plot=False)[0]])


    return user_data

def remove_baseline(t):
    fs = len(t[0])/12
    x_baseline = t[0][fs:2*fs]
    x_baseline = sum(x_baseline)/len(x_baseline)
    y_baseline = t[1][fs:2*fs]
    y_baseline = sum(y_baseline)/len(y_baseline)
    x = t[0][2*fs:]
    x = (x - x_baseline)*22.5
    y = t[1][2*fs:]
    y = (y - y_baseline)*13
    return x, y

def get_romberg(wbb_mgr_pre, wbb_mgr_post, username, sessiontype):

    results = pd.DataFrame()
    task_stanie_zgodny1_pre, task_stanie_zgodny2_pre, task_stanie_niezgodny1_pre, task_stanie_niezgodny2_pre, \
           task_bacznosc_zgodny1_pre, task_bacznosc_zgodny2_pre, task_bacznosc_niezgodny1_pre, task_bacznosc_niezgodny2_pre, \
           task_gabka_zgodny1_pre, task_gabka_zgodny2_pre, task_gabka_niezgodny1_pre, task_gabka_niezgodny2_pre = get_data(wbb_mgr_pre)
    task_stanie_zgodny1_post, task_stanie_zgodny2_post, task_stanie_niezgodny1_post, task_stanie_niezgodny2_post, \
           task_bacznosc_zgodny1_post, task_bacznosc_zgodny2_post, task_bacznosc_niezgodny1_post, task_bacznosc_niezgodny2_post, \
           task_gabka_zgodny1_post, task_gabka_zgodny2_post, task_gabka_niezgodny1_post, task_gabka_niezgodny2_post = get_data(wbb_mgr_post)

    for name, t in zip(['username', 'session_type'], [username, sessiontype]):
        results[name] = pd.Series([t])

    x, y = remove_baseline(task_pre)
    stanie_pre_path = wii_COP_path(wbb_mgr_pre, x, y, plot=False)[0]
    for name, t in zip(['stanie', 'oczy', 'bacznosc', 'gabka', 'poznawcze'],
                       [task_pre, task_oczy_pre, task_bacznosc_pre,
                        task_gabka_pre, task_poznawcze_pre]):
        x, y = remove_baseline(t)
        if len(x) < 490:
            results['{}_{}'.format(name, 'pre')] \
                = pd.Series([' '])
        else:
            results['{}_{}'.format(name, 'pre')] \
                = pd.Series(stanie_pre_path/wii_COP_path(wbb_mgr_pre, x, y, plot=False)[0])
    x, y = remove_baseline(task_post)
    stanie_post_path = wii_COP_path(wbb_mgr_post, x, y, plot=False)[0]
    for name, t in zip(['stanie', 'oczy', 'bacznosc', 'gabka', 'poznawcze'],
                       [task_post, task_oczy_post, task_bacznosc_post,
                        task_gabka_post, task_poznawcze_post]):
        x, y = remove_baseline(t)
        if len(x) < 490 or results[results['username']==username][name+'_pre'].values[0] == ' ':
            results['{}_{}'.format(name, 'post')] = pd.Series([' '])
            results['{}_{}'.format(name, 'pre')] = pd.Series([' '])
        else:
            results['{}_{}'.format(name, 'post')] \
                = pd.Series(stanie_post_path/[wii_COP_path(wbb_mgr_post, x, y, plot=False)][0])

    return results

if __name__ == '__main__':
    users = get_complete_users()

#    for user in users:
#        print(user)
#        w_pre, w_post = get_mgrs(user, after_tag_change=False)
#        adjust_timestamp(w_pre, user, 'pre')
#        adjust_timestamp(w_post, user, 'post')

    markers_path = pd.DataFrame()
    for user in users:
        w_pre, w_post = get_mgrs(user)
        markers_path = markers_path.append(get_markers(w_pre, w_post, user,
                                                       get_session_type(user)))
    markers_path.to_csv("./data/markers_path_dual.csv", sep=',')





