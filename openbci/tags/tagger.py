#!/usr/bin/env python
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
#      Mateusz Kruszynski <mateusz.kruszynski@gmail.com>
#

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client
import variables_pb2

from openbci.offline_analysis.obci_signal_processing import types_utils

import tags_logging as logger
LOGGER = logger.get_logger('tagger', 'info')

class Tagger(object):
    def __init__(self):
        """Initialize mx connection."""
        self._connection = connect_client(type = peers.TAGS_SENDER)

    def pack_tag(self, p_start_timestamp, p_end_timestamp, 
                 p_tag_name, p_tag_desc={}, p_tag_channels=""):
        """Return tag with given values. 
        Returned tag is serialised to string.
        Parameters:
        - p_start_timestamp - float 
        - p_end_timestamp - float
        - p_tag_name - string
        - p_tag_desc - dictionary
        - p_tag_channels - string like "0 6 7" - numbers of channels
        """
        l_tag = variables_pb2.Tag()
        l_tag.start_timestamp = p_start_timestamp
        l_tag.end_timestamp = p_end_timestamp
        l_tag.name = p_tag_name
        l_tag.channels = p_tag_channels
        for i_key, i_value in p_tag_desc.iteritems():
            l_new_var = l_tag.desc.variables.add()
            l_new_var.key = i_key
            l_new_var.value = types_utils.to_string(i_value)
        return l_tag.SerializeToString()
        
    def unpack_tag(self, p_tag_msg):
        """For given tag serialised to string, return tag as a dict with fields:
        - 'start_timestamp' - float
        - 'end_timestamp' - float
        - 'name' - string
        - 'desc' - dictionary
        """
        l_tag = variables_pb2.Tag()
        l_tag.ParseFromString(p_tag_msg)
        l_tag_dict = dict()
        l_tag_dict['start_timestamp'] = l_tag.start_timestamp
        l_tag_dict['end_timestamp'] = l_tag.end_timestamp
        l_tag_dict['name'] = l_tag.name
        l_tag_dict['channels'] = l_tag.channels
        l_tag_desc = dict()
        for i_var in l_tag.desc.variables:
            l_tag_desc[i_var.key] = i_var.value
        l_tag_dict['desc'] = l_tag_desc
        return l_tag_dict

    def send_tag(self, p_start_timestamp, p_end_timestamp, 
                 p_tag_name, p_tag_desc={}, p_tag_channels=""):
        """For given parameters create tag and send it to mx.
        Parameters:
        - p_start_timestamp - float 
        - p_end_timestamp - float
        - p_tag_name - string
        - p_tag_desc - dictionary
        - p_tag_channels - string like "0 6 7" - numbers of channels
        """
        l_info_desc = ''.join(
            ["Sending tag:\n",
             "start:", repr(p_start_timestamp),
             ", end:", repr(p_end_timestamp),
             ", name:", p_tag_name,
             ", channels:", p_tag_channels])
        LOGGER.debug(l_info_desc)
        LOGGER.debug(l_info_desc + "DESC: "+str(p_tag_desc))
        l_tag_msg = self.pack_tag(p_start_timestamp, p_end_timestamp,
                             p_tag_name, p_tag_desc, p_tag_channels)
        self._connection.send_message(
            message = l_tag_msg, 
            type=types.TAG, flush=True)

    def send_unpacked_tag(self, p_tag_dict):
        """A helper method to send tag in dictionary format."""
        self.send_tag(p_tag_dict['start_timestamp'],
                      p_tag_dict['end_timestamp'],
                      p_tag_dict['name'],
                      p_tag_dict.get('desc', {}),
                      p_tag_dict.get('channels', ''))
def get_tagger():
    return Tagger()
#def send_start_half_tag(p_timestamp, p_tag_name, p_tag_desc)
#    return id
#def send_end_half_tag(p_timestamp, p_tag_id, p_tag_desc)
#
