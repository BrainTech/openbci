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

import sys
#export PYTHONPATH=../../../:../../../openbci/:PYTHONPATH
sys.path.insert(1, '../../')
sys.path.insert(1, '../../openbci/')


from data_storage import csv_manager
from tags import tag_utils
from tags import svarog_tags_file_writer
from offline_analysis import offline_analysis_logging as logger
LOGGER = logger.get_logger("trigger_to_tag")

TEST = True
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
    >>> get_experiment_tags_from('exp.csv', ExperimentTag)[1].__dict__
    {'answer': u'3', 'group': u'Neg1', 'word': u'przemoc', 'word_time': u'0.03352157885988305', 'answer_time': u'1.0568231437235767'}

    """
    tags = []
    mgr = csv_manager.Reader(p_path, delimiter, quoting)
    hdr = [i for i in mgr.next() if len(i) > 0]
    for vals in mgr:
        tags.append(TagClass(hdr, vals))
    return tags
        
    

def get_trig(p_read_mgr):
    
    #tss = p_read_mgr.get_channel_values("TIMESTAMPS")
    
    trig = p_read_mgr.get_channel_values("TRIGGER")
    sampling = float(p_read_mgr.get_param('sampling_frequency'))
    tss = [i/sampling for i in range(len(trig))]
    
    ret_trig_change_tss = [tss[0]]
    ret_trig_values = [trig[0]]
    ret_trig_change_lens = []
    tr_prev = trig[0]
    tr_len = 1
    trig = trig[1:]
    tss = tss[1:]
    for i, tr in enumerate(trig):
        if tr != tr_prev:
            ret_trig_values.append(tr)
            ret_trig_change_tss.append(tss[i])
            ret_trig_change_lens.append(tr_len)
            tr_prev = tr
            tr_len = 0
        tr_len += 1

    ret_trig_change_lens.append(tr_len)
            
    return ret_trig_values, ret_trig_change_tss, ret_trig_change_lens




def get_tags_from_trigger(p_mgr, p_exp_tags, ignore_first=1, tag_len=1.0):
    """Create an svarog.tags file with tags determined by
    trigger channel and experiment data values

    >>> from data_storage import signalml_read_manager

    >>> mgr = signalml_read_manager.SignalmlReadManager('/media/windows/wiedza/bci/EKSPERYMENTY_DANE/kamil_pilot_25_11_2010/kamil_001.obci.svarog.info', '/media/windows/wiedza/bci/EKSPERYMENTY_DANE/kamil_pilot_25_11_2010/kamil_001.obci.dat')
    >>> mgr.start_reading()

    >>> exp_tags = get_experiment_tags_from('/media/windows/wiedza/bci/EKSPERYMENTY_DANE/kamil_pilot_25_11_2010/kamil_001.txt', KamilExpTag)

    >>> get_tags_from_trigger(mgr, exp_tags)

    """

    tag_samples_len = tag_len*float(p_mgr.get_param('sampling_frequency'))

    trig_vals, trig_tss, trig_lens = get_trig(p_mgr)

    trig_vals = trig_vals[ignore_first:]
    trig_tss = trig_tss[ignore_first:]
    trig_lens = trig_lens[ignore_first:]

    LOGGER.info("Tags in experiment file: "+str(len(p_exp_tags)))
    LOGGER.info("Trigger changes: "+str(len(trig_vals)))
    LOGGER.info("Above values should be even!!!!")

    tags = []
    for i, i_tag in enumerate(p_exp_tags):
        tag_name = i_tag.get_name()
        if not tag_name:
            tag_name = 'trigger'
        tag_desc = i_tag.get_desc()
        tags.append(tag_utils.pack_tag_to_dict(
                trig_tss[i], trig_tss[i]+tag_len, 
                tag_name, tag_desc))

        if trig_lens[i]/tag_samples_len < tag_len:
            LOGGER.warning(''.join[
                    "Warning!!!",
                    "Suspiciously short trigger length. You tried to build tags with length (seconds): ",
                    str(tag_len), " but trigger length (seconds) is: ", 
                    str(trig_lens[i]/tag_samples_len)])
    return tags

def create_tags_file(p_tags, p_path, p_first_sample_ts=0.0):
    wr = svarog_tags_file_writer.SvarogTagsFileWriter()
    for tag in p_tags:
        wr.tag_received(tag)
    wr.finish_saving(p_path, p_first_sample_ts)
    


def trigger_to_tag(p_new_tag_file_path, p_exp_file_path, p_info_file_path, p_data_file_path, p_ExpTagClass, ignore_first=1, tag_len=1.0):
    l_mgr = signalml_read_manager.SignalmlReadManager(p_info_file_path, p_data_file_path)
    l_mgr.start_reading()
    l_exp_tags = get_experiment_tags_from(p_exp_file_path, p_ExpTagClass)
    l_tags = get_tags_from_trigger(l_mgr, l_exp_tags, ignore_first, tag_len)
    create_tags_file(l_tags, p_new_tag_file_path)



def test():
    import doctest
    doctest.testmod(sys.modules[__name__])
    print("Tests succeeded!")


if __name__ == "__main__":
    if TEST:
        test()
    
