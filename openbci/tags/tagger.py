from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client
import variables_pb2

CONNECTION = connect_client(type = peers.TAGS_SENDER)

def pack_tag(p_start_timestamp, p_end_timestamp, p_tag_name, p_tag_desc):
    l_tag = variables_pb2.Tag()
    l_tag.start_timestamp = p_start_timestamp
    l_tag.end_timestamp = p_end_timestamp
    l_tag.name = p_tag_name
    for i_key, i_value in p_tag_desc.iteritems():
        l_new_var = l_tag.desc.variables.add()
        l_new_var.key = i_key
        l_new_var.value = str(i_value)
    return l_tag.SerializeToString()

def unpack_tag(p_tag_msg):
    l_tag = variables_pb2.Tag()
    l_tag.ParseFromString(p_tag_msg)
    l_tag_dict = dict()
    l_tag_dict['start_timestamp'] = l_tag.start_timestamp
    l_tag_dict['end_timestamp'] = l_tag.end_timestamp
    l_tag_dict['name'] = l_tag.name
    l_tag_desc = dict()
    for i_var in l_tag.desc.variables:
        l_tag_desc[i_var.key] = i_var.value
    l_tag_dict['desc'] = l_tag_desc
    return l_tag_dict

def send_tag(p_start_timestamp, p_end_timestamp, p_tag_name, p_tag_desc):
    l_tag_msg = pack_tag(p_start_timestamp, p_end_timestamp, 
                                  p_tag_name, p_tag_desc)
    CONNECTION.send_message(
                message = l_tag_msg, 
                type=types.TAG, flush=True)
