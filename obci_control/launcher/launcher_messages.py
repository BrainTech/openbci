#!/usr/bin/python
# -*- coding: utf-8 -*-

##### MACHINE -- CONTROLLER #######

message_templates = {
	"register_peer" : dict(peer_type='', uuid='', rep_addrs='', pub_addrs='', name='', other_params=''),
	#TODO delete
	"create_experiment" : dict(launch_file='', sandbox_dir='')
	"experiment_created" : dict(name='', uuid='', rep_addrs='')


	"start_peer" : None,
	"kill_peer" : None,
	"start_experiment" : None,
	"kill_experiment" : None,


}

error_codes = ["invalid_supervisor_data",
				"main_supervisor_already_exists",
				"unsupported_peer_type"]