#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
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
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

import sys, os.path, settings

from data_storage import csv_manager
from openbci.offline_analysis.obci_signal_processing import read_manager
from openbci.offline_analysis.obci_signal_processing.tags import tag_utils
from openbci.offline_analysis.obci_signal_processing.tags import tags_file_writer

import trigger
from offline_analysis import offline_analysis_logging as logger
LOGGER = logger.get_logger("trigger_experiment")

class ExperimentTag(object):
    def __init__(self, keys, values):
        for i, key in enumerate(keys):
            setattr(self, key, values[i])

    def get_name(self):
        return None

    def get_desc(self):
        return self.__dict__


class KamilExpTag(ExperimentTag):
    def get_name(self):
        return self.group[:3]


def get_experiment_tags_from(p_path, TagClass, quoting=0, delimiter=','):
    """
    >>> get_experiment_tags_from(os.path.join(settings.module_abs_path(), 'tests', 'exp.csv'), ExperimentTag)[1].__dict__
    {'answer': u'3', 'group': u'Neg1', 'word': u'przemoc', 'word_time': u'0.03352157885988305', 'answer_time': u'1.0568231437235767'}

    """
    tags = []
    mgr = csv_manager.Reader(p_path, delimiter, quoting)
    hdr = [i for i in mgr.next() if len(i) > 0]
    for vals in mgr:
        tags.append(TagClass(hdr, vals))
    return tags
        
    
def get_tags_from_trigger(p_mgr, p_exp_tags, ignore_first=0, ignore_last=0, tag_len=1.0, min_trig_len=0.0, ignore_from_sample_number=None):
    """Create an svarog.tags file with tags determined by
    trigger channel and experiment data values
    >>> from openbci.offline_analysis.obci_signal_processing import read_manager

    >>> mgr = read_manager.ReadManager('/media/windows/wiedza/bci/EKSPERYMENTY_DANE/kamil_pilot_25_11_2010/kamil_001.obci.svarog.info', '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/kamil_pilot_25_11_2010/kamil_001.obci.dat', None)

    >>> exp_tags = get_experiment_tags_from('/media/windows/wiedza/bci/EKSPERYMENTY_DANE/kamil_pilot_25_11_2010/kamil_001.txt', KamilExpTag)

    #>>> len(get_tags_from_trigger(mgr, exp_tags))
    #72

    >>> len(get_tags_from_trigger(mgr, exp_tags, 2, 1, 1.0, 0.5))
    72

    """
    tag_samples_len = tag_len*float(p_mgr.get_param('sampling_frequency'))
    first_ts = float(p_mgr.get_param('first_sample_timestamp'))
    sampling = float(p_mgr.get_param('sampling_frequency'))

    trig_vals, trig_tss, trig_lens = trigger.get_trigger(p_mgr, min_trig_len, spare_memory=True)
    
    l_exp_tags = list(p_exp_tags)
    if ignore_from_sample_number:
        ignore_from_ts = ignore_from_sample_number/sampling - first_ts
        for i in enumerate(len(trig_tss)):
            if trig_tss[i] > ignore_from_ts:
                trig_vals = trig_vals[:i]
                trig_tss = trig_tss[:i]
                trig_lens = trig_lens[:i]
                l_exp_tags = l_exp_tags[:i]
                break
        
    if ignore_last > 0:
        trig_vals = trig_vals[ignore_first:-ignore_last]
        trig_tss = trig_tss[ignore_first:-ignore_last]
        trig_lens = trig_lens[ignore_first:-ignore_last]
    else:
        trig_vals = trig_vals[ignore_first:]
        trig_tss = trig_tss[ignore_first:]
        trig_lens = trig_lens[ignore_first:]
        
    LOGGER.info("Trigger lengths " +str(trig_lens))

    LOGGER.info("Tags in experiment file: "+str(len(l_exp_tags)))
    LOGGER.info("Trigger changes: "+str(len(trig_vals)))
    LOGGER.info("Above values should be even!!!!")

    if len(l_exp_tags) > len(trig_vals):
        LOGGER.error(''.join(["Number of tags in experiment is bigger than",
                              " number of trigger changes.",
                              " Processing aborted!"]))
        sys.exit(1)

    tags = []
    for i, i_tag in enumerate(l_exp_tags):
        tag_name = i_tag.get_name()
        if not tag_name:
            tag_name = 'trigger'
        tag_desc = i_tag.get_desc()
        tags.append(tag_utils.pack_tag_to_dict(
                trig_tss[i], trig_tss[i]+tag_len, 
                tag_name, tag_desc))

        if trig_lens[i]/tag_samples_len < tag_len:
            LOGGER.warning(''.join([
                    "Warning!!!",
                    "Suspiciously short trigger length. You tried to build tags with length (seconds): ",
                    str(tag_len), " but trigger length (seconds) is: ", 
                    str(trig_lens[i]/tag_samples_len)]))
    return tags

def create_tags_file(p_tags, p_path, p_first_sample_ts=0.0):
    """
    >>> create_tags_file([{'channels': '', 'start_timestamp': 1088.654296875, 'desc': {'answer': u'2', 'group': u'Neu2', 'word': u'programowanie', 'word_time': u'0.032020550097854539', 'answer_time': u'0.41630263064155315'}, 'name': u'Neu', 'end_timestamp': 1089.654296875}, {'channels': '', 'start_timestamp': 1093.279296875, 'desc': {'answer': u'2', 'group': u'Neu2', 'word': u'milczenie', 'word_time': u'0.032006581842097148', 'answer_time': u'0.59216995456131372'}, 'name': u'Neu', 'end_timestamp': 1094.279296875}], './test.tags')

    >>> from tags import tags_file_reader

    >>> rd = tags_file_reader.TagsFileReader('./test.tags')

    >>> tags = rd.get_tags()

    >>> tags[0]
    {'channels': '', 'start_timestamp': 1088.654296875, 'desc': {u'answer': u'2', u'answer_time': u'0.41630263064155315', u'word': u'programowanie', u'word_time': u'0.032020550097854539', u'group': u'Neu2'}, 'name': u'Neu', 'end_timestamp': 1089.654296875}

    >>> tags[1]
    {'channels': '', 'start_timestamp': 1093.279296875, 'desc': {u'answer': u'2', u'answer_time': u'0.59216995456131372', u'word': u'milczenie', u'word_time': u'0.032006581842097148', u'group': u'Neu2'}, 'name': u'Neu', 'end_timestamp': 1094.279296875}

    >>> import os

    >>> os.remove('test.tags')
    """

    wr = tags_file_writer.TagsFileWriter(p_path)
    for tag in p_tags:
        wr.tag_received(tag)
    wr.finish_saving(p_first_sample_ts)
    


def trigger_to_tag(p_new_tag_file_path, p_exp_file_path, p_info_file_path, p_data_file_path, p_ExpTagClass, 
                   p_ignore_first=0, p_ignore_last=0, p_tag_len=1.0, p_min_trig_len=0.0):
    """
    >>> trigger_to_tag('test.tags', '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/kamil_pilot_25_11_2010/kamil_001.txt', '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/kamil_pilot_25_11_2010/kamil_001.obci.svarog.info', '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/kamil_pilot_25_11_2010/kamil_001.obci.dat', KamilExpTag, 2, 1, 1.0, 0.5)

    >>> import os

    #>>> os.remove('test.tags')
    """
    l_mgr = read_manager.ReadManager(p_info_file_path, p_data_file_path, None)

    l_exp_tags = get_experiment_tags_from(p_exp_file_path, p_ExpTagClass)
    l_tags = get_tags_from_trigger(l_mgr, l_exp_tags, p_ignore_first, p_ignore_last, p_tag_len, p_min_trig_len)
    create_tags_file(l_tags, p_new_tag_file_path)



def test():
    import doctest
    doctest.testmod(sys.modules[__name__])
    print("Tests succeeded!")


if __name__ == "__main__":
    test()
    
