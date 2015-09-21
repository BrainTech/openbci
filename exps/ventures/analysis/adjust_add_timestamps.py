#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:
#       Mateusz Biesaga <mateusz.biesaga@gmail.com>
#

from __future__ import print_function, division
from obci.analysis.balance.wii_analysis import *
from obci.analysis.balance.wii_preprocessing import *
from obci.analysis.obci_signal_processing.tags import tags_file_writer as tags_writer
from obci.analysis.obci_signal_processing.tags import tag_utils
import analysis_helper

def adjust_timestamp(w, user, prefix):
    """
    Adjusts timestamps in order to provide the ability of comparing tags
    and raw signal (Psychopy tags may start in a different moment, this
    function is created to overcome that effect).
    Also, this function adds the additional tags before and after every
    single task.
    :param w: WBBReadManager object
    :param user: User name
    :param prefix: 'pre' or 'post'
    :return: File adjusted_tag.tag in a proper directory.
    """
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



if __name__ == '__main__':
    users = analysis_helper.get_complete_users('dual_data')

    for user in users:
        print(user)
        w_pre, w_post = analysis_helper.get_read_managers_by_user(user, after_tag_change=False)
        adjust_timestamp(w_pre, user, 'pre')
        adjust_timestamp(w_post, user, 'post')






