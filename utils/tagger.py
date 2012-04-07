#!/usr/bin/env python
#
# Author:
#      Mateusz Kruszynski <mateusz.kruszynski@titanis.pl>
#
from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_client import ConfiguredClient
from configs import variables_pb2, settings

from utils import tags_helper

class Tagger(ConfiguredClient):
    def __init__(self, addresses):
        super(Tagger, self).__init__(addresses=addresses,
                                     type=peers.TAGS_SENDER)
        self.ready()

    def send_tag(self, p_start_timestamp, p_end_timestamp, 
                 p_tag_name, p_tag_desc={}, p_tag_channels=""):
        tags_helper.send_tag(self.conn, p_start_timestamp, p_end_timestamp,
                 p_tag_name, p_tag_desc, p_tag_channels)

def get_tagger():
    return Tagger(settings.MULTIPLEXER_ADDRESSES)

