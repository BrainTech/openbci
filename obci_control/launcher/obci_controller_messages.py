#!/usr/bin/python
# -*- coding: utf-8 -*-

import json

##### MACHINE -- CONTROLLER #######

BASIC_MSG = dict(type='', sender='', receiver='')

message_templates = {
	"register_machine" : dict(uuid='', address='', rep_port='', pub_port='', name='', main=''),
	"ok" : dict(),
	"error" : dict(err_code='', request='', details=''),
	"start_peer" : None,
	"kill_peer" : None,
	"start_obci_instance" : None,
	"kill_obci_instance" : None,
	"kill" : None,
	"heartbeat" : None,
	"ping" : None
}

def fill_msg(msg_type, **kwargs):
	if msg_type not in message_templates:
		raise OBCIMessageError()
	msg = message_templates[msg_type].copy()
	msg.update(BASIC_MSG)
	msg['type'] = msg_type

	for key, value in kwargs.iteritems():
		if key not in msg:
			raise OBCIMessageError()
		msg[key] = value
	return json.dumps(msg)

def decode_msg(msg):
	return json.loads(msg)


class OBCIMessageError(Exception):
	pass