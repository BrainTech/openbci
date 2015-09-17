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

def estimate_fs(TSS_samples):
    durations = []
    for ind in range(1, len(TSS_samples)):
        durations.append(TSS_samples[ind]-TSS_samples[ind-1])
    return 1.0/np.mean(durations)

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
                                         w.mgr.get_tags()[i]['name'] + str(i),
                                         {'znaczenie': w.mgr.get_tags()[i]['desc']['znaczenie'],
                                          'czcionka': w.mgr.get_tags()[i]['desc']['czcionka']})
            writer.tag_received(tag)
    writer.finish_saving(0.0)

def get_short_data(wbb_mgr):
    results = []
    tags = wbb_mgr.mgr.get_tags()
    previous_tag = 0
    for tag in tags:
        if previous_tag:

            fragment = wii_cut_fragments(wbb_mgr, start_tag_name=previous_tag['name'],
                                         end_tags_names=[tag['name']], TS=True)
            results.append(fragment)
        previous_tag = tag
    return results
    """
    results[2:13] - ss_zgodny1
    results[16:27]
    results[30:41]
    results[44:55]

    results[60:71]
    results[74:85]
    results[88:99]
    results[102:113]

    results[118:129]
    results[132:143]
    results[146:157]
    results[160:171]
    """

def count_area(start, stop, data):
    area = []
    for i in range(start, stop):
        if data[i].any():
            x = data[i][0]*22.5
            y = data[i][1]*13
            area.append(wii_confidence_ellipse_area(x, y))
    return area

def show_plots(data_pre, data_post, user):
    plt.gcf().set_size_inches(12, 10)
    for i in range(3):
        if i == 0:
            titlee = 'stanie'
        elif i == 1:
            titlee = 'bacznosc'
        else:
            titlee = 'gabka'
        plt.subplot(3, 2, i*2+1)
        area = count_area((58*i)+3, (58*i)+56, data_pre)
        plt.plot(area, 'o-')
        plt.ylim(0, 5)
        plt.xlim(0, 47)
        plt.axvspan(11, 23, color='red', alpha=0.3)
        plt.axvspan(35, 47, color='red', alpha=0.3)
        plt.title(titlee+'_pre')
        plt.subplot(3, 2, i*2+2)
        area = count_area((58*i)+3, (58*i)+56, data_post)
        plt.plot(area, 'o-')
        plt.ylim(0, 5)
        plt.xlim(0, 47)
        plt.axvspan(11, 23, color='red', alpha=0.3)
        plt.axvspan(35, 47, color='red', alpha=0.3)
        plt.title(titlee+'_post')
    plt.suptitle(user + ' - ' + get_session_type(user))
    plt.savefig('./plots/'+user+'.png', dpi=120)
    plt.show()
    plt.close()

if __name__ == '__main__':
    users = get_complete_users()

    """
    for user in users:
        print(user)
        w_pre, w_post = get_mgrs(user, after_tag_change=False)
        adjust_timestamp(w_pre, user, 'pre')
        adjust_timestamp(w_post, user, 'post')
    """

    markers_path = pd.DataFrame()
    for user in users:
        print(user)
        w_pre, w_post = get_mgrs(user)
        data_pre = get_short_data(w_pre)
        data_post = get_short_data(w_post)
        show_plots(data_pre, data_post, user)












