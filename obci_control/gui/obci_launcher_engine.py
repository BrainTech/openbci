#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide import QtCore
import zmq
import threading

import common.net_tools as net
from common.message import send_msg, recv_msg

from launcher.obci_client import OBCIClient
import launcher.obci_script as obci_script
import launcher.launcher_tools as launcher_tools
import launcher.system_config as system_config
import launcher.launch_file_parser as launch_file_parser



class OBCILauncherEngine(QtCore.QObject):
	update_ui = QtCore.Signal(object)
	obci_state_change = QtCore.Signal(object)

	internal_msg_templates = {
		'_launcher_engine_msg' : dict(task='', pub_addr='')
	}

	def __init__(self, obci_client):
		super(OBCILauncherEngine, self).__init__()

		self.client = obci_client
		self.ctx = obci_client.ctx

		self.mtool = self.client.mtool
		self.mtool.add_templates(self.internal_msg_templates)

		self.experiments = {}

		self.obci_poller = zmq.Poller()

		self.monitor_push = self.ctx.socket(zmq.PUSH)
		self.monitor_addr = 'inproc://obci_monitor'
		self.monitor_push.bind(self.monitor_addr)

		self._stop_monitoring = False
		self.obci_monitor_thr = threading.Thread(target=self.obci_monitor, 
												args=[self.ctx, self.monitor_addr])
		self.obci_monitor_thr.daemon = True
		self.obci_monitor_thr.start()

		self.obci_state_change.connect(self.handle_obci_state_change)
		# server req -- list_experiments
		# subscribe to server PUB
		# for each exp -- 
		#		req - detailed info
		#		initialise from launcher_info
		#		for each peer:
		#			update params and data from peer_info (params, machine, status)
		#		subscribe to experiment PUB


	def obci_monitor(self, ctx, pull_addr):
		pull = ctx.socket(zmq.PULL)
		pull.connect(pull_addr)

		subscriber = ctx.socket(zmq.SUB)
		subscriber.setsockopt(zmq.SUBSCRIBE, "")

		poller = zmq.Poller()
		poller.register(pull, zmq.POLLIN)
		poller.register(subscriber, zmq.POLLIN)

		subscriber.connect(net.server_address(sock_type='pub'))

		def handle_msg(msg):
			if msg.type == '_launcher_engine_msg':
				if msg.task == 'connect':
					subscriber.connect(msg.pub_addr)
			else:
				self.obci_state_change.emit(msg)

		while not self._stop_monitoring:
			try:
				socks = dict(poller.poll(timeout=200))
			except:
				break
			
			for socket in socks:
				if  socks[socket] == zmq.POLLIN:
					msg = self.mtool.unpack_msg(recv_msg(socket))
					print "\n\nengine!!! got: ", msg, '\n\n'
					handle_msg(msg)


	def handle_obci_state_change(self, launcher_message):
		"engine signallllllllled", launcher_message
		self.update_ui.emit(launcher_message)

	def list_experiments(self):

		exp_list = self.client.send_list_experiments()
	
		exps = []
		print exp_list.exp_data, exp_list.exp_data.__class__
		for uid, exp_data in exp_list.exp_data.iteritems():
			for_gui = self._exp_for_gui(exp_data)
			exps.append(for_gui)
			exp_rep = self.ctx.socket(zmq.REP)
			for addr in exp_data['rep_addrs']:
				exp_rep.connect(addr)

			for addr in exp_data['pub_addrs']:
				print "       *******************     ", addr
				send_msg(self.monitor_push, self.mtool.fill_msg('_launcher_engine_msg',
													task='connect', pub_addr=addr))
			for_gui['rep_sock'] = exp_rep

			# self.existing_exps[uid] = 
		return exps
		# {'name':'scenario1', 'status':'running', 'tooltip':u'Przejęcie kontroli nad światem', 
		#  'bg':'green', 'info':u"Zarabiamy, kase budujemy armie i <b>PODBIJAMY ŚWIAT</b>"}

	def _experiment_info(self, exp_gui_data):
		pass

	def _exp_for_gui(self, exp_detail):
		print exp_detail
		info = dict(name=exp_detail['name'],
					status=exp_detail['status_name'],
					path=exp_detail['launch_file_path'],
					params={},
					tooltip='Ole!',
					bg='green',
					info=u'ĄŚŻŹĆŃÓŁĘ')
		return info

class ExperimentEngineInfo(QtCore.QObject):
	def __init__(self, launch_file_path=None, preset_name=None, launcher_data=None, ctx=None):
		self.launch_file = launch_file_path
		self.launcher_data = launcher_data
		self.name = preset_name

		self.ctx = ctx
		self.exp_req = None

		self.status = launcher_tools.ExperimentStatus()
		self.exp_config = system_config.OBCIExperimentConfig()

		if launcher_data is not None:
			self._name = launcher_data['name']
			self.launch_file = launcher_data['launch_file_path']
			self.ctx = self.ctx if self.ctx is not None else zmq.Context()
			self.exp_req = self.ctx.socket(zmq.REQ)
			for addr in launcher_data['rep_addrs']:
				self.exp_req.connect(addr)
	
			self.exp_config.uuid = launcher_data['uuid']
			self.exp_config.origin_machine = launcher_data['origin_machine']

		self.exp_config.launch_file_path = self.launch_file

		#TODO in future -- obtain whole config through socket
		result, details = self.make_experiment_config()
		self.exp_config.status(self.status)
		self.status.details = details


	#FIXME  !!! copy-paste from obci_experiment
	def make_experiment_config(self):
		launch_parser = launch_file_parser.LaunchFileParser(
							launcher_tools.obci_root(), settings.DEFAULT_SCENARIO_DIR)
		if not self.launch_file:
			return False, "Empty scenario."
		try:
			with open(self.launch_file) as f:
				print "launch file opened"
				launch_parser.parse(f, self.exp_config)
		except Exception as e:
			self.status.set_status(launcher_tools.NOT_READY, details=str(e))

			return False, str(e)

		#print self.exp_config
		rd, details = self.exp_config.config_ready()
		if rd:
			self.status.set_status(launcher_tools.READY_TO_LAUNCH)
		else:
			self.status.set_status(launcher_tools.NOT_READY, details=details)

		return True, None

	def _get_experiment_details(self, req_sock):
		pass

	def _get_peer_details(self, req_sock):
		pass

	def updatable(self, peer_id, config_part, **kwargs):
		return False

	def update_peer_param(self, peer_id, param, value):
		pass

	def update_experiment_details(self):
		pass

	def update_peers(self):
		pass

	def update(self):
		pass