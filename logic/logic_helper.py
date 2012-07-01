#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>
import os
import subprocess
import common.config_message as cmsg
from common.message import OBCIMessageTool
from launcher.launcher_messages import message_templates
from launcher.launcher_tools import obci_root
import peer.peer_cmd as peer_cmd

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client
from configs import settings

mtool = OBCIMessageTool(message_templates)

def restart_scenario(conn, new_scenario, comment="Wait...", leave_on=[], overwrites=[]):
	"""
	new_scenario: scenario_path relative to obci_root
	overwrites:   {'peer_id' : ['-p', 'param_name', 'param_value', 
									'-p', 'etc', 'etc',
								'-f' 'config_ini_file_path_relative_to_obci_root']}

	leave_on:  ['list', 'of', 'peer_ids', 'which', 'are', 'in', 'both', 'scenarios',
					'and', 'we', 'do','not', 'want', 'them', 'to', 'restart']
	"""

	if new_scenario.startswith('/') or new_scenario.startswith('~'):
		new_scenario = os.path.expanduser(new_scenario)
	else:
		new_scenario = os.path.join(obci_root(), new_scenario)

	conf_msg = cmsg.fill_msg(types.GET_CONFIG_PARAMS,
				 sender='',
				 param_names=['experiment_uuid'],
				 receiver='config_server')

	try:
		reply = conn.query(message=conf_msg,
				   type=types.GET_CONFIG_PARAMS)
	except OperationFailed:
		print "OperationFailed (in restart_scenario) Could not connect to config server"
		reply = None
	except OperationTimedOut:
		print  "Operation timed out! (in restart_scenario) (could not connect to config server)"
		reply = None

	if reply == None:
		return

	if reply.type == types.CONFIG_ERROR:
		print "(in restart_scenario) could not acquire current experiment uuid"
		return

	elif reply.type == types.CONFIG_PARAMS:
		reply_msg = cmsg.unpack_msg(reply.type, reply.message)
		params = cmsg.params2dict(reply_msg)
		if not 'experiment_uuid' in params:
			print "no experiment_uuid!!!"
		else:
			uid = params['experiment_uuid']
			if not uid:
				print 'experiment uuid unset!!!'
			else:
				ovr_list = ['--ovr']

				for peer in overwrites:
					scan = overwrites[peer]
					params = overwrites[peer]
					cut = 0
					while scan:
						if '-f' in scan:
							ind = scan.index('-f')
							params[cut+ind+1] = os.path.join(obci_root(), params[cut+ind+1])
							cut = cut+ind+1
							scan = params[cut:]
						else: break

					# for i in range(len(params)):
					# 	params[i] = params[i].replace(" ", "\ ")
					# 	print params[i]


					ovr_list += ['--peer', peer]
					ovr_list += params

				# leave_on_str = '' if not leave_on else ' --leave_on ' + ' '.join(leave_on)
				# overwr_str = '' if not overwrites else ' '.join(ovr_list)
				# command = "sleep 0.5 && obci morph " + str(uid) + " " + new_scenario + \
				# 		" " + leave_on_str  + overwr_str + " &"
				

				subpr_call = ['obci', 'morph', str(uid), new_scenario, '--leave_on'] + leave_on + ovr_list
				print "---------------\n", subpr_call, "\n--------------"
				subprocess.call(subpr_call)
				# os.system(command)


    #os.system("sleep 0.5 && obci srv_kill && sleep 10 && obci launch "+new_scenario+" &")    
