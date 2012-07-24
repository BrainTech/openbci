#!/usr/bin/env python
#
# Author:
#      Mateusz Kruszynski <mateusz.kruszynski@titanis.pl>
#

from multiplexer.multiplexer_constants import peers, types
from analysis.obci_signal_processing import types_utils

from obci_configs import variables_pb2
from utils import openbci_logging as logger

LOGGER = logger.get_logger('tags_helper', 'info')

def pack_tag_from_tag(tag_dict):
    return pack_tag(tag_dict['start_timestamp'], tag_dict['end_timestamp'],
                    tag_dict['name'], tag_dict['desc'], tag_dict['channels'])

def pack_tag(p_start_timestamp, p_end_timestamp, 
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
        
def unpack_tag(p_tag_msg):
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

def send_tag(conn, p_start_timestamp, p_end_timestamp, 
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
    l_tag_msg = pack_tag(p_start_timestamp, p_end_timestamp,
                              p_tag_name, p_tag_desc, p_tag_channels)
    conn.send_message(
        message = l_tag_msg, 
        type=types.TAG, flush=True)

def send_unpacked_tag(p_tag_dict):
    """A helper method to send tag in dictionary format."""
    send_tag(p_tag_dict['start_timestamp'],
             p_tag_dict['end_timestamp'],
             p_tag_dict['name'],
             p_tag_dict.get('desc', {}),
             p_tag_dict.get('channels', ''))
