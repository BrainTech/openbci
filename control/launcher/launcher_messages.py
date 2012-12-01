#!/usr/bin/python
# -*- coding: utf-8 -*-

##### MACHINE -- CONTROLLER #######

message_templates = {
    "register_peer" : dict(peer_type='', uuid='', rep_addrs='', pub_addrs='', name='', other_params=''),

    "create_experiment" : dict(launch_file='', sandbox_dir='', name='', overwrites='', serialized_scenario=''),
    "experiment_created" : dict(name='', uuid='', rep_addrs='', pub_addrs='', origin_machine='',
                                    status_name='', details='', launch_file_path='',
                                    tcp_addrs='', ip=''),
    "list_experiments" : dict(),
    "running_experiments" : dict(exp_data='', nearby_machines=''),

    "get_experiment_info" : dict(),
    "experiment_info" : dict(experiment_status='', launch_file_path='', scenario_dir='',
                         origin_machine='',    peers='', unsupervised_peers='', uuid='', status='',
                         name=''),

    "get_peer_info" : dict(peer_id=''),
    "get_peer_param_values" : dict(peer_id=''),
    "peer_param_values" : dict(peer_id='', param_values=''),
    "peer_info" : dict(config_sources='',
        external_params='',
        launch_dependencies='',
        local_params='',
               machine='',
        path='',
        peer_id='',
        peer_type=''),
    "get_experiment_scenario" : dict(),
    "experiment_scenario" : dict(scenario='', launch_file_path='', uuid=''),
    "set_experiment_scenario" : dict(scenario='', launch_file_path=''),

    "obci_control_message" : dict(peer_name='', peer_type='',severity='', msg_code='',
                                launcher_message='', params='', details=''),
    "experiment_status_change" : dict(uuid='', status_name='', details='', peers=''),
    "experiment_info_change" : dict(uuid='', name='', launch_file_path=''),
    "experiment_transformation" : dict(uuid='', status_name='', details='', name='',
                                    launch_file='', old_name='', old_launch_file=''),

    "get_experiment_contact" : dict(strname=''),
    "experiment_contact" : dict(name='', uuid='', rep_addrs='', pub_addrs='', tcp_addrs='', machine='', status_name='', details=''),

    "launch_process" : dict(proc_type='', name='', path='', args='', machine_ip='',
                                    capture_io='', stdout_log='', stderr_log=''),
    "launched_process_info" : dict(machine='', pid='', path='', args='', name='', proc_type='', details=''),
    "kill_process" : dict(machine='', pid=''),

    "launch_error" : dict(err_code='', details=''),
    "all_peers_launched": dict(machine=''),
    "obci_launch_failed" : dict(machine='', path='', args='', details=''),

    "start_experiment" : dict(),
    "starting_experiment" : dict(),
    "experiment_launch_error": dict(err_code='', details=''),
    "process_supervisor_registered" : dict(machine_ip=''),

    "kill_experiment" : dict(strname='', force=''),
    "kill_sent" : dict(experiment_id=''),

    "start_mx" : dict(args=''),
    "start_peers" : dict(mx_data='', add_launch_data=''),
    "manage_peers" : dict(kill_peers='', start_peers_data=''),
    "dead_process" : dict(machine='', pid='', status=''),

    "obci_peer_dead" : dict(path='', peer_id='', status='', experiment_id=''),
    "stop_all" : dict(),

    "get_tail" : dict(peer_id='', len=''),
    "tail" : dict(txt='', experiment_id='', peer_id=''),

    "join_experiment" : dict(peer_id='', peer_type='', path=''),
    "leave_experiment" : dict(peer_id=''),

    "add_peer": dict(peer_id='', peer_path='', peer_type='', machine='', param_overwrites='', 
                                custom_config_path='', config_sources='', launch_dependencies='',
                                 apply_globals=''),
    "kill_peer": dict(peer_id='', remove_config=''),
    "_kill_peer": dict(peer_id='', machine=''),
    "new_peer_added": dict(uuid='', peer_id='', config='', peer_path='', machine='',status_name=''),

    "obci_peer_params_changed" : dict(peer_id='', params=''),
    "obci_peer_registered" : dict(peer_id='', params=''),
    "obci_peer_unregistered" : dict(peer_id=''),
    "obci_peer_ready" : dict(peer_id=''),

    "update_peer_config" : dict(peer_id='', local_params='',
                            external_params='', launch_dependencies='', config_sources=''),
    "save_scenario" : dict(file_name='', force=''),

    "find_eeg_experiments" : dict(client_push_address='', checked_srvs=''),
    "eeg_experiments" : dict(experiment_list=''),

    "find_eeg_amplifiers" : dict(client_push_address='', amplifier_types=''),
    "eeg_amplifiers" : dict(amplifier_list=''),
    "start_eeg_signal" : dict(client_push_address='', amplifier_params='', launch_file='', name=''),
    "launcher_shutdown" : dict(),

    "server_broadcast" : dict(rep_port='', pub_port=''),

    "experiment_finished" : dict(details=''),
    "morph_to_new_scenario" : dict(launch_file='', name='', overwrites='', leave_on=''),
    "list_nearby_machines" : dict(),
    "nearby_machines" : dict(nearby_machines='')



}

error_codes = ["invalid_supervisor_data",
                "main_supervisor_already_exists",
                "unsupported_peer_type",
                "launch_error",
                "start_experiment_error",
                "create_supervisor_error"]

if __name__ == '__main__':
    import common.message as msg
    import json
    tool = msg.OBCIMessageTool(message_templates)
    used = []
    for temp in [msg.common_templates, message_templates]:
        for msg in temp:
            if not msg in used:
                print '//-------------------------   ', msg, '- full   ---------------------'
                print tool.fill_msg(msg)
                print '//--', msg, '- without base   -----'
                st = json.dumps(temp[msg], indent=4)
                print st
                used.append(msg)
