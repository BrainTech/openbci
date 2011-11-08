#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import types
import common.cfg_messages_pb2 as templates
import json

MX_CFG_TYPES = [types.GET_CONFIG_PARAMS,
					types.CONFIG_PARAMS,
					types.REGISTER_PEER_CONFIG,
					types.PEER_REGISTERED,
					types.UPDATE_PARAMS,
					types.PARAMS_CHANGED,
					types.PEER_READY,
					types.PEER_READY_QUERY,
					types.READY_STATUS]

MX_CFG_MESSAGES = {
	types.GET_CONFIG_PARAMS : templates.ConfigParamsRequest,
	types.CONFIG_PARAMS : templates.ConfigParams,
	types.REGISTER_PEER_CONFIG : templates.ConfigParams,
	types.PEER_REGISTERED : templates.PeerIdentity,
	types.UPDATE_PARAMS: templates.ConfigParams,
	types.PARAMS_CHANGED : templates.ConfigParams,
	types.PEER_READY : templates.PeerIdentity,
	types.PEER_READY_QUERY : templates.PeerIdentity,
	types.READY_STATUS : templates.PeerIdentity
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
	msg = msg_for_type(mx_type)
	if msg is None:
		raise ConfigMessageError()
	return __pb2_construct(msg, kwargs)

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

###############################################################
#### OBSOLETE code, will be deleted

MSG_PARTS = 4
MSG_DELIMITERS_N = MSG_PARTS - 1
TYPE = 0
RECEIVER = 1
SENDER = 2
MESSAGE = 3

DM = ':'


class ConfigMessage(object):

	def __init__(self):
		self.type = ''
		self.receiver = ''
		self.sender = ''
		self.message = ''

	def __repr__(self):
		return repr(vars(self))

	def unpack(self, p_msg):
		msg = p_msg.split(DM, MSG_DELIMITERS_N)
		if len(msg) != MSG_PARTS:
			print "BAD MSG: ",p_msg
			raise ConfigMessageError

		self.type = msg[TYPE]
		self.receiver = msg[RECEIVER]
		self.sender = msg[SENDER]
		self.message = msg[MESSAGE]

	def pack(self):
		return DM.join([self.type, self.receiver, self.sender, self.message])


class ConfigMessageError(Exception):
	pass