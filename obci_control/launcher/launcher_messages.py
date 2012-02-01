#!/usr/bin/python
# -*- coding: utf-8 -*-

##### MACHINE -- CONTROLLER #######

message_templates = {
	"register_peer" : dict(peer_type='', uuid='', rep_addrs='', pub_addrs='', name='', other_params=''),

	"create_experiment" : dict(launch_file='', sandbox_dir='', name=''),
	"experiment_created" : dict(name='', uuid='', rep_addrs='', pub_addrs='', machine=''),
	"list_experiments" : dict(),
	"running_experiments" : dict(exp_data=''),

	"get_experiment_info" : dict(),
	"experiment_info" : dict(experiment_status='', launch_file_path='', scenario_dir='',
						 origin_machine='',	peers='', unsupervised_peers='', uuid=''),

	"get_peer_info" : dict(peer_id=''),
	"peer_info" : dict(peer_info=''),

	"get_experiment_contact" : dict(strname=''),
	"experiment_contact" : dict(name='', uuid='', rep_addrs='', pub_addrs='', machine=''),

	"launch_process" : dict(proc_type='', name='', path='', args='', machine_ip='',
									capture_io='', stdout_log='', stderr_log=''),
	"launched_process_info" : dict(machine='', pid='', path='', args='', name='', proc_type='', details=''),
	"kill_process" : dict(),
	"restart_process" : dict(),
	"launch_error" : dict(err_code='', details=''),
	"all_peers_launched": dict(machine=''),
	"obci_launch_failed" : dict(machine='', path='', args='', details=''),

	"start_experiment" : dict(),
	"starting_experiment" : dict(),
	"experiment_launch_error": dict(err_code='', details=''),
	"process_supervisor_registered" : dict(machine_ip=''),

	"kill_experiment" : dict(strname='', force=''),
	"kill_sent" : dict(),

	"start_mx" : dict(args=''),
	"start_peers" : dict(mx_data=''),
	"dead_process" : dict(machine='', pid='', status=''),

	"obci_peer_dead" : dict(path='', peer_id='', status=''),
	"stop_all" : dict(),

	"get_tail" : dict(peer_id='', len=''),
	"tail" : dict(txt='', experiment_id='', peer_id=''),

	"join_experiment" : dict(peer_id='', peer_type='', path=''),
	"leave_experiment" : dict(peer_id=''),

	"obci_peer_params_changed" : dict(peer_id='', params=''),
	"obci_peer_registered" : dict(peer_id='', params=''),
	"obci_peer_unregistered" : dict(peer_id=''),
	"obci_peer_ready" : dict(peer_id='')

}

error_codes = ["invalid_supervisor_data",
				"main_supervisor_already_exists",
				"unsupported_peer_type",
				"launch_error",
				"start_experiment_error",
				"create_supervisor_error"]