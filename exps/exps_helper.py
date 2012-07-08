#!/usr/bin/env python
#
# Author:
#      Mateusz Kruszynski <mateusz.kruszynski@titanis.pl>
#
from utils import tagger
from acquisition import acquisition_helper

class ExpsHelper(object):
    def __init__(self):
        self.tagger = tagger.get_tagger()

    def send_tag(self, p_start_timestamp, p_end_timestamp, 
                 p_tag_name, p_tag_desc={}, p_tag_channels=""):
        self.tagger.send_tag(p_start_timestamp, p_end_timestamp, 
                 p_tag_name, p_tag_desc, p_tag_channels)

    def finish_saving(self, wait=True):
        if wait:
            acquisition_helper.finish_saving()
        else:
            acquisition_helper.send_finish_saving(self.tagger.conn)
