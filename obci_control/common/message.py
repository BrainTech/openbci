#!/usr/bin/python
# -*- coding: utf-8 -*-

import json


BASIC_MSG = dict(type='', sender='', receiver='')

common_templates = {
	"rq_ok" : dict(status=''),
	"rq_error" : dict(err_code='', request='', details=''),
	"kill" : None,
	"heartbeat" : None,
	"ping" : None,
	"pub_addr_rq" : dict(),
	"pub_addr" : dict(pub_addresses='', request='')
}

common_errors = ["invalid_msg_format",
				"incomplete_message",
				"unsupported_msg_type",
				"no_pub_sock"]

class OBCIMessageTool(object):
	def __init__(self, msg_templates, errors=[]):
		self.templates = common_templates
		self.templates.update(msg_templates)
		self.errors = common_errors
		self.errors.append(errors)

	def fill_msg(self, msg_type, **kwargs):
		if msg_type not in self.templates:
			raise OBCIMessageError()
		msg = self.templates[msg_type].copy()
		msg.update(BASIC_MSG)
		msg['type'] = msg_type

		for key, value in kwargs.iteritems():
			if key not in msg:
				raise OBCIMessageError()
			msg[key] = value
		return json.dumps(msg)

	def decode_msg(self, msg):
		return json.loads(msg)

def send_msg(sock, message):
	return sock.send_unicode(message)

def recv_msg(sock):
	return sock.recv_unicode()


class OBCIMessageError(Exception):
	pass