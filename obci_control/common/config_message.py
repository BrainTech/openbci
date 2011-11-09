#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import types
import common.cfg_messages_pb2 as templates
import json
from google.protobuf.message import Message

MX_CFG_MESSAGES = {
	types.GET_CONFIG_PARAMS : templates.ConfigParamsRequest,
	types.CONFIG_PARAMS : templates.ConfigParams,
	types.REGISTER_PEER_CONFIG : templates.ConfigParams,
	types.UNREGISTER_PEER_CONFIG : templates.PeerIdentity,
	types.PEER_REGISTERED : templates.PeerIdentity,
	types.UPDATE_PARAMS: templates.ConfigParams,
	types.PARAMS_CHANGED : templates.ConfigParams,
	types.PEER_READY : templates.PeerIdentity,
	types.PEERS_READY_QUERY : templates.PeerReadyQuery,
	types.READY_STATUS : templates.PeerReadyStatus,
	types.CONFIG_ERROR : templates.ConfigError
}

def msg_for_type(mx_type):
	msg = MX_CFG_MESSAGES.get(mx_type, None)
	return msg() if msg is not None else None

def unpack_msg(mx_type, msg_str):
	msg = msg_for_type(mx_type)
	if msg is None:
		raise ConfigMessageError()
	msg.ParseFromString(msg_str)
	return msg


def fill_msg(mx_type, **kwargs):
	"""This does NOT encode any values to json!"""
	msg = msg_for_type(mx_type)
	if msg is None:
		raise ConfigMessageError()
	return __pb2_construct(msg, **kwargs)

def pack_msg(msg):
	return msg.SerializeToString()

def fill_and_pack(mx_type, **kwargs):
	return pack_msg(fill_msg(mx_type, **kwargs))

def val2str(value):
	return json.dumps(value)

def str2val(string):
	return json.loads(string)

def __pb2_construct(what, **kwargs):
	#copied from k2launcher.utils
	#TODO cleaner

    w = what
    for k in kwargs:
        v = kwargs[k]
        if type(v) == list:
            p = w.__getattribute__(k)
            for l in v:
                p.append(l)
        elif isinstance(v, Message):
            w.__getattribute__(k).CopyFrom(v)
        else:
            w.__setattr__(k, v)
    return w

def __msg_to_dict(msg, val_f=None):
	fun = val_f if val_f else lambda x: x
	def upd(dic, p):
		dic.update({p[0].name: fun(p[1])})
		return dic

	d = reduce(upd, msg.ListFields(), {})
	return d

def msg_to_dict(msg, val_f=None):
	"""Does not convert nested messages!"""
	dic = __msg_to_dict(msg, val_f)
	return dic

def __param2msg(param, value):
	return __pb2_construct(templates.Param(), name=param, value=value)


def params2dict(config_params_msg):
	"""Take parameters from the config_params_msg,
	put them in a dictionary (with decoded values from json) and return it.
	The message should have a 'params' attribute"""
	dic = {}
	for par_msg in config_params_msg.params:
		dic[par_msg.name] = str2val(par_msg.value)
	return dic


def dict2params(dic, config_params_msg):
	"""Take parameters from the dictionary dic, encode values to json and
	put them in the config_params_msg. The message should have
	a 'params' attribute"""
	for name in dic:
		par_msg = config_params_msg.params.add()
		par_msg.name = name
		par_msg.value = val2str(dic[name])


class ConfigMessageError(Exception):
	pass

if __name__ == '__main__':
	msg = fill_msg(types.PEER_READY, peer_id="dupa")
	print msg

	print msg_to_dict(msg)
	msg2 = fill_msg(types.GET_CONFIG_PARAMS,
					sender="ja", receiver="ty", param_names=["par1", "par2"])
	print msg_to_dict(msg2)
	print msg2

	msg3 = fill_msg(types.CONFIG_PARAMS,
					sender="ja", receiver="ty")

	dict2params(dict(asdf=123, sdfg="alalala"), msg3)

	print params2dict(msg3)
