#!/usr/bin/python
# -*- coding: utf-8 -*-

##### MACHINE -- CONTROLLER #######

message_templates = {
	"register_peer" : dict(peer_type='', uuid='', rep_addrs='', pub_addrs='', name='', other_params=''),

	"create_experiment" : dict(launch_file='', sandbox_dir=''),
	"experiment_created" : dict(name='', uuid='', rep_addrs='', pub_addrs='', machine=''),
	"list_experiments" : dict(),
	"running_experiments" : dict(exp_data=''),
	"get_experiment_info" : dict(peer_id=''),
	"experiment_info" : dict(exp_info=''),
	"get_experiment_contact" : dict(strname=''),
	"experiment_contact" : dict(name='', uuid='', rep_addrs='', pub_addrs='', machine=''),

	"launch_process" : dict(path='', args='', must_register='',),
	"launched_process_info" : dict(machine='', pid='', path='', args=''),

	"start_experiment" : dict(),
	"starting_experiment" : dict(),
	"kill_experiment" : dict(strname='', force=''),
	"kill_sent" : dict()

}

error_codes = ["invalid_supervisor_data",
				"main_supervisor_already_exists",
				"unsupported_peer_type",
				"launch_error",
				"start_experiment_error",
				"create_supervisor_error",
				"launch_supervisor_os_error"]