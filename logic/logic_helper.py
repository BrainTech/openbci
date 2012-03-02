#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>
import os
import common.config_message as cmsg
from common.message import OBCIMessageTool
from launcher.launcher_messages import message_templates
import peer.peer_cmd as peer_cmd

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client
from configs import settings

mtool = OBCIMessageTool(message_templates)

def restart_scenario(conn, new_scenario, comment="Wait..."):

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
				os.system("sleep 0.5 && obci morph " + str(uid) + " " + new_scenario + " &")


    #os.system("sleep 0.5 && obci srv_kill && sleep 10 && obci launch "+new_scenario+" &")    
