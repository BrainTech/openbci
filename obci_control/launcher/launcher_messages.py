#!/usr/bin/python
# -*- coding: utf-8 -*-

##### MACHINE -- CONTROLLER #######

message_templates = {
	"register_peer" : dict(peer_type='', uuid='', rep_addrs='', pub_addrs='', name='', other_params=''),
	#TODO delete
	"register_supervisor" : dict(uuid='', rep_addrs='', pub_addrs='', name='', main=''),
	"register_experiment" : dict(uuid='', rep_addrs='', pub_addrs='', name=''),
	"start_peer" : None,
	"kill_peer" : None,
	"start_obci_instance" : None,
	"kill_obci_instance" : None,

	"create_experiment" : dict()
}

error_codes = ["invalid_supervisor_data",
				"main_supervisor_already_exists",
				"unsupported_peer_type"]