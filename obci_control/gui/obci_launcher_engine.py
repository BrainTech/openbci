#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore
import zmq
import threading
import ConfigParser
import codecs
import os

import common.net_tools as net
from common.message import send_msg, recv_msg, OBCIMessageTool, PollingObject
import common.obci_control_settings as settings

from launcher.obci_client import OBCIClient
from launcher.launcher_messages import message_templates
import launcher.obci_script as obci_script
import launcher.launcher_tools as launcher_tools
import launcher.system_config as system_config
import launcher.launch_file_parser as launch_file_parser
import peer.peer_cmd as peer_cmd


PRESETS = 'obci_control/gui/presets.ini'
MODE_BASIC = 'basic'
MODE_ADVANCED = 'advanced'
MODE_EXPERT = 'expert'
MODES = [MODE_BASIC, MODE_ADVANCED]#, MODE_EXPERT]

class OBCILauncherEngine(QtCore.QObject):
	update_ui = QtCore.pyqtSignal(object)
	obci_state_change = QtCore.pyqtSignal(object)

	internal_msg_templates = {
		'_launcher_engine_msg' : dict(task='', pub_addr='')
	}
	

	def __init__(self, obci_client):
		super(OBCILauncherEngine, self).__init__()

		self.client = obci_client
		self.ctx = obci_client.ctx

		self.mtool = self.client.mtool
		self.mtool.add_templates(self.internal_msg_templates)

		self.preset_path = os.path.join(launcher_tools.obci_root(), PRESETS)
		self.experiments = self.prepare_experiments()

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

		for exp in self.experiments:
			if exp.launcher_data is not None:
				self._exp_connect(exp.launcher_data)

		self.details_mode = MODE_ADVANCED

		# server req -- list_experiments
		# subscribe to server PUB
		# for each exp -- 
		#		req - detailed info
		#		initialise from launcher_info
		#		for each peer:
		#			update params and data from peer_info (params, machine, status)
		#		subscribe to experiment PUB

	def exp_ids(self):
		ids = {}
		for i, e in enumerate(self.experiments):
			ids[e.uuid] = i
		return ids

	def index_of(self, exp_uuid):
		if exp_uuid in self.exp_ids():
			return self.exp_ids()[exp_uuid]
		else:
			return None

	def prepare_experiments(self):
		experiments = []
		presets = self._parse_presets(self.preset_path)
		for preset in presets:
			exp = ExperimentEngineInfo(preset_data=preset, ctx=self.ctx)
			experiments.append(exp)

		running = self._list_experiments()
		for exp in running:
			matches = [(i, e) for i, e in enumerate(experiments) if\
						e.name == exp['name'] and e.preset_data is not None]
			if matches:
				index, preset = matches.pop()
				preset.setup_from_launcher(exp, preset=True)
			else:
				experiments.append(ExperimentEngineInfo(launcher_data=exp, ctx=self.ctx))

		return experiments

	def _exp_connect(self, exp_data):
		for addr in exp_data['pub_addrs']:
			send_msg(self.monitor_push, self.mtool.fill_msg('_launcher_engine_msg',
												task='connect', pub_addr=addr))		

	def _parse_presets(self, preset_path):
		preset_file = codecs.open(preset_path, encoding='utf-8')
		parser = ConfigParser.RawConfigParser()
		parser.readfp(preset_file)
		presets = []
		for sec in parser.sections():
			pres = {'name' : sec}
			for opt in parser.options(sec):
				pres[opt] = parser.get(sec, opt)
			presets.append(pres)
		return presets


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
					handle_msg(msg)

	def handle_obci_state_change(self, launcher_message):
		type_ = launcher_message.type
		if type_ == 'experiment_created':
			self._handle_experiment_created(launcher_message)

		elif type_ == 'launcher_shutdown':
			self._handle_launcher_shutdown(launcher_message)

		elif type_ == 'kill_sent':
			self._handle_kill_sent(launcher_message)

		elif type_ == 'kill':
			self._handle_kill(launcher_message)

		elif type_ == 'obci_control_message': #obci_peer_registered, obci_peer_params_changed
			self._handle_obci_control_message(launcher_message)

		elif type_ == 'experiment_status_change':
			self._handle_experiment_status_change(launcher_message)

		elif type_ == 'obci_peer_dead':
			self._handle_obci_peer_dead(launcher_message)

		self.update_ui.emit(launcher_message)
		print "----engine signalled", type_

	def _handle_experiment_created(self, msg, exp_list=None):
		exps = exp_list if exp_list else self.experiments

		matches = [(i, e) for i, e in enumerate(exps) if\
						e.name == msg.name and e.preset_data is not None]

		if matches:
			index, exp = matches.pop()
			exp.setup_from_launcher(msg.dict(), preset=True)
		else:
			exps.append(ExperimentEngineInfo(launcher_data=msg.dict(), ctx=self.ctx))

		self._exp_connect(msg.dict())


	def _handle_launcher_shutdown(self, msg):
		self.experiments = []
		presets = self._parse_presets(self.preset_path)
		for preset in presets:
			exp = ExperimentEngineInfo(preset_data=preset, ctx=self.ctx)
			self.experiments.append(exp)

	def _handle_kill_sent(self, msg):
		uid = msg.experiment_id
		index = self.index_of(uid)
		if index is not None:
			exp = self.experiments[index]
		
			if exp.preset_data:
				exp.setup_from_preset(exp.preset_data)
				exp.launcher_data = None
			else:
				del exp

	def _handle_kill(self, msg):
		pass

	def _handle_obci_control_message(self, msg):
		uid = msg.sender
		index = self.index_of(uid)
		if index is not None:
			exp = self.experiments[index]
		
			if msg.msg_code in ["obci_peer_registered", "obci_peer_params_changed"]:
				for par, val in msg.launcher_message['params'].iteritems():
					exp.update_peer_param(msg.launcher_message['peer_id'], 
											par,
											val,
											runtime=True)

	def _handle_experiment_status_change(self, msg):
		uid = msg.uuid
		index = self.index_of(uid)
		if index is not None:
			exp = self.experiments[index]
			exp.status.set_status(msg.status_name, msg.details)
			if msg.peers:
				for peer, status in msg.peers.iteritems():
					exp.status.peer_status(peer).set_status(status)

	def _handle_obci_peer_dead(self, msg):
		uid = msg.experiment_id
		index = self.index_of(uid)
		if index is not None:
			print "&&&&&&&&&&&&&&&&  obci peer dead"
			exp = self.experiments[index]
		
			status_name = msg.status[0]
			details = msg.status[1]
			st = exp.status
			st.peer_status(msg.peer_id).set_status(status_name, details)

	def list_experiments(self):
		return self.experiments

	def _list_experiments(self):
		exp_list = self.client.send_list_experiments()
		exps = []
		for exp_data in exp_list.exp_data.values():
			exps.append(exp_data)
		return exps

	def reset_launcher(self, msg):

		self.client.srv_kill()
		running = obci_script.server_process_running()
		if running:
			print "reset_launcher: something went wrong... SERVER STILL RUNNIN"

		self.client = obci_script.client_server_prep()
		self.experiments = self.prepare_experiments()

	def stop_experiment(self, msg):
		uid = str(msg)
		index = self.index_of(uid)
		if index is None:
			print "experiment uuid not found: ", uid
			return
		exp = self.experiments[index]
		if not exp.launcher_data:
			print "this exp is not running...", uid
			return

		self.client.kill_exp(exp.uuid)


	def start_experiment(self, msg):
		uid = str(msg)
		index = self.index_of(uid)
		if index is None:
			print "experiment uuid not found: ", uid
			return
		exp = self.experiments[index]
		if exp.launcher_data:
			print "already running"
			return

		args = exp.get_launch_args()
		self.client.launch(**args)



class ExperimentEngineInfo(QtCore.QObject):
	def __init__(self, preset_data=None, launcher_data=None, ctx=None):
		self.preset_data = preset_data
		self.launch_file = None
		self.launcher_data = launcher_data
		self.name = None
		self.info = ""
		self.public_params = []
		self.origin_machine = ''
		self.unsupervised_peers = {}
		self.old_uid = None

		self.ctx = ctx
		self.exp_req = None
		self.mtool = OBCIMessageTool(message_templates)
		self.poller = PollingObject()

		if preset_data is not None:
			self.setup_from_preset(preset_data)

		elif launcher_data is not None:
			self.setup_from_launcher(launcher_data)


	def setup_from_preset(self, preset_data, launcher=False):
		self.preset_data = preset_data
		self.overwrites = {}
		self.runtime_changes = {}

		self.status = launcher_tools.ExperimentStatus()
		self.exp_config = system_config.OBCIExperimentConfig()

		self.name = preset_data['name']
		self.launch_file = preset_data['launch_file']
		self.info = preset_data['info']
		self.public_params = [p.strip() for p in preset_data['public_params'].split(',')]
		self.exp_config.uuid = self.name + '--' + self.launch_file

		result, details = self._make_config()

		self.status.details = details
		self._set_public_params()


	def setup_from_launcher(self, launcher_data, preset=False):
		self.launcher_data = launcher_data
		self.runtime_changes = {}
		if preset:
			self.old_uid = self.exp_config.uuid
		else:
			self.overwrites = {}
			self.status = launcher_tools.ExperimentStatus()
			self.exp_config = system_config.OBCIExperimentConfig()	
		
		self.name = launcher_data['name']# if not preset else self.old_uid
		self.launch_file = launcher_data['launch_file_path']
		self.ctx = self.ctx if self.ctx is not None else zmq.Context()
		self.exp_req = self.ctx.socket(zmq.REQ)
		for addr in launcher_data['rep_addrs']:
			self.exp_req.connect(addr)

		self.exp_config.uuid = launcher_data['uuid']
		self.exp_config.origin_machine = launcher_data['origin_machine']

		result, details = self._make_config()

		self.status.set_status(launcher_data['status_name'], details=launcher_data['details'])
		self._get_experiment_details()
		self._set_public_params()

	def _set_public_params(self):
		for par in self.public_params:
			if len(par.split('.')) == 2:
				[peer, param] = par.split('.')
				self.exp_config.peers[peer].public_params.append(param)

	def _make_config(self):

		self.exp_config.launch_file_path = self.launch_file
		self.uuid = self.exp_config.uuid

		#TODO in future -- obtain whole config through socket if possible
		result, details = self.make_experiment_config()

		self.exp_config.status(self.status)
		return result, details


	#FIXME  !!! copy-paste from obci_experiment
	def make_experiment_config(self):
		launch_parser = launch_file_parser.LaunchFileParser(
							launcher_tools.obci_root(), settings.DEFAULT_SCENARIO_DIR)
		if not self.launch_file:
			return False, "Empty scenario."

		try:
			with open(os.path.join(launcher_tools.obci_root(), self.launch_file)) as f:
				launch_parser.parse(f, self.exp_config)
		except Exception as e:
			self.status.set_status(launcher_tools.NOT_READY, details=str(e))
			print "config errror   ", str(e)
			return False, str(e)

		rd, details = self.exp_config.config_ready()
		if rd:
			self.status.set_status(launcher_tools.READY_TO_LAUNCH)
		else:
			self.status.set_status(launcher_tools.NOT_READY, details=details)
			print rd, details

		return True, None

	def _get_experiment_details(self):
		if not self.exp_req:
			return
		exp_msg = self.comm_exp(self.mtool.fill_msg("get_experiment_info"))
		if not exp_msg:
			return

		self.origin_machine = exp_msg.origin_machine

		for peer, short_info in exp_msg.peers.iteritems():
			# self.exp_config.set_peer_machine(peer, short_info['machine'])

			msg = self.comm_exp(self.mtool.fill_msg("get_peer_info",
										peer_id=peer))
			if not msg:
				return

			ext_defs = {}
			for name, defi in msg.external_params.iteritems():
				ext_defs[name] = defi[0] + '.' + defi[1]
			self.exp_config.update_peer_config(peer, dict(config_sources=msg.config_sources,
												launch_dependencies=msg.launch_dependencies,
												local_params=msg.local_params,
												external_params=ext_defs))
		
		for peer, status in exp_msg.experiment_status['peers_status'].iteritems():
			self.status.peer_status(peer).set_status(
											status['status_name'],
											details=status['details'])

	def parameters(self, peer_id, mode):

		params = {}
		peer = self.exp_config.peers[peer_id]
		if mode == MODE_BASIC:
			for par in peer.public_params:
				params[par] = (self.exp_config.param_value(peer_id, par), None)
		else:
			params = peer.config.local_params
			for param in peer.config.local_params:
				params[param] = (self.exp_config.param_value(peer_id, param), None)
			for param, defi in peer.config.ext_param_defs.iteritems():
				params[param] = (self.exp_config.param_value(peer_id, param), defi[0]+'.'+defi[1])
		return params


	def comm_exp(self, msg):
		send_msg(self.exp_req, msg)
		response, _ = self.poller.poll_recv(self.exp_req, timeout=3000)
		if not response:
			return None
		return self.mtool.unpack_msg(response)


	def updatable(self, peer_id, config_part, **kwargs):
		return False

	def update_peer_param(self, peer_id, param, value, runtime=False):
		changes = self.overwrites if not runtime else self.runtime_changes

		ovr = changes.get(peer_id, None)
		ovr = ovr if ovr is not None else {}
		if param not in ovr:
			old = self.exp_config.param_value(peer_id, param)
			if old != value:
				ovr[param] = old
				changes[peer_id] = ovr

		self.exp_config.update_local_param(peer_id, param, value)


	def get_launch_args(self):
		d = dict(launch_file=self.launch_file, name=self.name)
		args = ['--ovr']
		if self.overwrites:
			for peer_id in self.overwrites:
				args.append('--peer')
				args.append(peer_id)

				for arg in self.overwrites[peer_id]:
					args += ['-p', arg, self.exp_config.param_value(peer_id, arg)]
		pack = peer_cmd.peer_overwrites_pack(args)
		d['overwrites'] = pack
		return d

	def peer_info(self, peer_id):
		return self.exp_config.peers[peer_id]
