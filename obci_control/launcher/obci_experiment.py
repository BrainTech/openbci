#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import uuid
import argparse
import subprocess
import threading

import zmq

from common.message import OBCIMessageTool, send_msg, recv_msg, PollingObject
from launcher_messages import message_templates
import common.net_tools as net
import common.obci_control_settings as settings

from obci_control_peer import OBCIControlPeer, basic_arg_parser
from subprocess_monitor import SubprocessMonitor, TimeoutDescription,\
STDIN, STDOUT, STDERR, NO_STDIO
from obci_control_peer import RegistrationDescription
import subprocess_monitor

import launch_file_parser
import launcher_tools
import system_config
import obci_process_supervisor

import peer.peer_cmd as peer_cmd

REGISTER_TIMEOUT = 25

class OBCIExperiment(OBCIControlPeer):

	msg_handlers = OBCIControlPeer.msg_handlers.copy()

	def __init__(self, obci_install_dir, sandbox_dir, launch_file=None,
										source_addresses=None,
										source_pub_addresses=None,
										rep_addresses=None,
										pub_addresses=None,
										name='obci_experiment',
										launch=False,
										overwrites=None):

		###TODO TODO TODO !!!!
		###cleaner subclassing of obci_control_peer!!!
		self.source_pub_addresses = source_pub_addresses
		self.origin_machine = net.ext_ip(ifname=net.server_ifname())
		self.poller = PollingObject()
		self.launch_file = launch_file
		super(OBCIExperiment, self).__init__(obci_install_dir,
											source_addresses,
											rep_addresses,
											pub_addresses,
											name)
		self.sandbox_dir = sandbox_dir if sandbox_dir else settings.DEFAULT_SANDBOX_DIR

		self.supervisors = {} #machine -> supervisor contact/other info
		self._wait_register = 0
		self.sv_processes = {} # machine -> Process objects)
		self.unsupervised_peers = {}

		self.subprocess_mgr = SubprocessMonitor(self.ctx, self.uuid)

		self.status = launcher_tools.ExperimentStatus()

		self.exp_config = system_config.OBCIExperimentConfig(uuid=self.uuid)
		self.exp_config.origin_machine = self.origin_machine
		self.exp_config.launch_file_path = self.launch_file

		result, details = self.make_experiment_config()
		if overwrites:
			try:
				for [ovr, other] in overwrites:
					self.exp_config.update_peer_config(other['peer_id'], ovr)
					if other['config_file']:
						for f in other['config_file']:
							self.exp_config.file_update_peer_config(other['peer_id'], f)
			except Exception, e:
				details = str(e)

		self.exp_config.status(self.status)
		self.status.details = details
		self.status_changed(self.status.status_name, self.status.details)
		if not result and self.launch_file:
			print "- - - - - - -  LAUNCH FILE INVALID!!!  - - - - - - - "
			print "status:", self.status.as_dict(), details



		self.mx_addr = None
		self.mx_pass = None


	def net_init(self):
		self.source_sub_socket = self.ctx.socket(zmq.SUB)
		self.source_sub_socket.setsockopt(zmq.SUBSCRIBE, "")

		if self.source_pub_addresses:
			for addr in self.source_pub_addresses:
				self.source_sub_socket.connect(addr)
		self._all_sockets.append(self.source_sub_socket)

		(self.supervisors_rep, self.supervisors_rep_addrs) = self._init_socket(
									[],
									zmq.REP)
		(self.supervisors_sub, self.supervisors_sub_addrs) = (self.ctx.socket(zmq.SUB), [])

		self._all_sockets.append(self.supervisors_sub)
		self._all_sockets.append(self.supervisors_rep)

		super(OBCIExperiment, self).net_init()

	def params_for_registration(self):
		return dict(pid=os.getpid(), origin_machine=self.origin_machine,
				status_name='', details='', launch_file_path=self.launch_file)

	def custom_sockets(self):
		return [self.source_sub_socket, self.supervisors_sub, self.supervisors_rep]

	def args_for_process_sv(self, machine, local=False):
		args = ['--sv-addresses']
		sv_rep_ = net.choose_not_local(self.supervisors_rep_addrs)
		if not sv_rep_ or local:
			sv_rep_ = net.choose_local(self.supervisors_rep_addrs)

		args += sv_rep_[:1]
		args.append('--sv-pub-addresses')
		pub_addrs = net.choose_not_local(self.pub_addresses)
		if not pub_addrs or local:
			pub_addrs = net.choose_local(self.pub_addresses, ip=True)

		args += pub_addrs[:1] #self.pub_addresses
		args += [
					'--obci-dir', self.obci_dir,
					'--sandbox-dir', str(self.sandbox_dir),
					'--name', os.path.basename(self.launch_file) +\
							 '-' + self.uuid.split('-',1)[0] + \
							'-' + machine
					]
		return args


	def _start_obci_process_supervisor(self, machine_addr):
		args = self.args_for_process_sv(machine_addr)
		proc_type = 'obci_process_supervisor'

		if machine_addr == self.origin_machine:
			path = obci_process_supervisor.__file__
			path = '.'.join([path.rsplit('.', 1)[0], 'py'])
			sv_obj, details = self.subprocess_mgr.new_local_process(path, args,
															proc_type=proc_type,
															capture_io=NO_STDIO)
		else:
			conn_addr = 'tcp://' + machine_addr + ':' + net.server_rep_port()
			sv_obj, details = self.subprocess_mgr.new_remote_process(path=None,
												args=args, proc_type=proc_type,
												name=self.uuid, machine_ip=machine_addr,
												conn_addr=conn_addr, capture_io=NO_STDIO
												)
		if sv_obj is None:
			return False, details

		timeout_handler = TimeoutDescription(timeout=REGISTER_TIMEOUT,
						timeout_method=self._handle_register_sv_timeout,
						timeout_args=[sv_obj])
		sv_obj.set_registration_timeout_handler(timeout_handler)
		self.sv_processes[machine_addr] = sv_obj
		return sv_obj, None

	def _start_all_obci_process_supervisors(self):
		self._wait_register = len(self.exp_config.peer_machines())
		details = None

		for machine in self.exp_config.peer_machines():
			result, details = self._start_obci_process_supervisor(machine)

			if not result:
				self.status.set_status(launcher_tools.FAILED_LAUNCH, details)
				details = "{0} [{1}], FAILED to start supervisor: {2}".format(
											self.name, self.peer_type(), details)
				print details
				self.status_changed(self.status.status_name, self.status.details)
				return False, details

			k = result.machine_ip
			self.sv_processes[k] = result
		return True, details

	def _send_launch_data(self):
		pass

	def _start_experiment(self):
		"""
		START EXPERIMENT!!!!
		##################################################################
		"""
		result, details = self._start_all_obci_process_supervisors()
		if not result:
			send_msg(self._publish_socket, self.mtool.fill_msg("experiment_launch_error",
												sender=self.uuid, details=details,
												err_code='supervisor_launch_error'))


		return result, details

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

	def status_changed(self, status_name, details, peers=None):
		send_msg(self.source_req_socket, self.mtool.fill_msg('experiment_status_change',
				status_name=status_name, details=details, uuid=self.uuid, peers=peers))
		self.poller.poll_recv(self.source_req_socket, timeout=8000)


	def peer_type(self):
		return 'obci_experiment'


	@msg_handlers.handler('register_peer')
	def handle_register_peer(self, message, sock):
		"""Experiment"""
		if message.peer_type == "obci_process_supervisor":

			machine, pid = message.other_params['machine'], message.other_params['pid']

			if message.other_params['mx_data'][0] is not None and not self.mx_addr:
				## right now we support only one mx per obci instance
				self.mx_addr = message.other_params['mx_data'][0]
				self.mx_pass = message.other_params['mx_data'][1]

			proc = self.subprocess_mgr.process(machine, pid)
			if proc is None:
				send_msg(sock, self.mtool.fill_msg("rq_error",
								err_code='process_not_found', request=message.dict()))
				return

			status, details = proc.status()
			if status != subprocess_monitor.UNKNOWN:
				send_msg(sock, self.mtool.fill_msg("rq_error",
								err_code='process_status_invalid', request=message.dict(),
								details=(status, details)))
				send_msg(self._publish_socket, self.mtool.fill_msg("experiment_launch_error",
												sender=self.uuid, details=(status, details),
												err_code='registration_error'))
				return

			desc = self.supervisors[message.other_params['machine']] = \
							RegistrationDescription(
												message.uuid,
												message.name,
												message.rep_addrs,
												message.pub_addrs,
												message.other_params['machine'],
												message.other_params['pid'])
			proc.registered(desc)
			a = self._choose_process_address(proc, desc.pub_addrs)
			if a is not None:
				self.supervisors_sub_addrs.append(a)
				self.supervisors_sub.setsockopt(zmq.SUBSCRIBE, "")
				self.supervisors_sub.connect(a)
				print "{0} [{1}], Connecting to supervisor pub address {2}".format(
								self.name, self.peer_type(), a)

			launch_data = self.exp_config.launch_data(machine)

			send_msg(sock, self.mtool.fill_msg("rq_ok", params=launch_data))

			# inform observers
			send_msg(self._publish_socket, self.mtool.fill_msg("process_supervisor_registered",
												sender=self.uuid,
												machine_ip=desc.machine_ip))

			self._wait_register -= 1
			if self._wait_register == 0:
				send_msg(self._publish_socket, self.mtool.fill_msg("start_mx",
										args=self.mx_args()))

	def mx_args(self):
		return ["run_multiplexer", self.mx_addr,
				'--multiplexer-password', self.mx_pass,
				'--rules', launcher_tools.mx_rules_path()]

	@msg_handlers.handler("launched_process_info")
	def handle_launched_process_info(self, message, sock):
		if message.proc_type == 'multiplexer':
			self._wait_register = len(self.exp_config.peer_machines())
			send_msg(self._publish_socket, self.mtool.fill_msg('start_peers',
											mx_data=self.mx_args()))
		elif message.proc_type == 'obci_peer':
			pass
		self.status.peer_status(message.name).set_status(
											launcher_tools.RUNNING)
		self.status_changed(self.status.status_name, self.status.details,
			peers={message.name : self.status.peer_status(message.name).status_name})


	@msg_handlers.handler("all_peers_launched")
	def handle_all_peers_launched(self, message, sock):

		self._wait_register -= 1
		print self.name,'[', self.type, ']',  message, self._wait_register
		if self._wait_register == 0:
				self.status.set_status(launcher_tools.RUNNING)
				self.status_changed(self.status.status_name, self.status.details)

	def _choose_process_address(self, proc, addresses):
		print self.name,'[', self.type, ']', "(exp) choosing sv address:", addresses
		addrs = []
		chosen = None
		if proc.is_local():
			addrs = net.choose_local(addresses)
		if not addrs:
			addrs = net.choose_not_local(addresses)
		if addrs:
			chosen = addrs.pop()
		return chosen

	@msg_handlers.handler('get_experiment_info')
	def handle_get_experiment_info(self, message, sock):
		## a not-launched version
		# exp_info = self.exp_config.info()
		# exp_info['experiment_status'] = self.status.as_dict()
		# exp_info['unsupervised_peers'] = self.unsupervised_peers


		send_msg(self._publish_socket, self.mtool.fill_msg('rq_ok'))
		send_msg(sock, self.mtool.fill_msg('experiment_info',
											experiment_status=self.status.as_dict(),
											unsupervised_peers=self.unsupervised_peers,
											origin_machine=self.exp_config.origin_machine,
											uuid=self.exp_config.uuid,
											scenario_dir=self.exp_config.scenario_dir,
											peers=self.exp_config.peers_info(),
											launch_file_path=self.exp_config.launch_file_path,
											name=self.name))

	@msg_handlers.handler('get_peer_info')
	def handle_get_peer_info(self, message, sock):
		if message.peer_id not in self.exp_config.peers:
			send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
						err_code='peer_id_not_found'))
		else:
			peer_info = self.exp_config.peers[message.peer_id].info(detailed=True)
			send_msg(sock, self.mtool.fill_msg('peer_info', **peer_info))


	@msg_handlers.handler('get_peer_param_values')
	def handle_get_peer_param_values(self, message, sock):
		if message.peer_id not in self.exp_config.peers:
			send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
						err_code='peer_id_not_found'))
		else:
			peer_id = message.peer_id
			vals = self.exp_config.all_param_values(peer_id)
			send_msg(sock, self.mtool.fill_msg('peer_param_values', 
										peer_id=peer_id,param_values=vals,
										sender=self.uuid))


	@msg_handlers.handler('get_peer_config')
	def handle_get_peer_config(self, message, sock):
		send_msg(sock, self.mtool.fill_msg('ping', sender=self.uuid))



	@msg_handlers.handler('start_experiment')
	def handle_start_experiment(self, message, sock):
		if not self.status.status_name == launcher_tools.READY_TO_LAUNCH:
			send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
											err_code='exp_status_'+self.status.status_name,
											details=self.status.details))
		else:
			self.status.set_status(launcher_tools.LAUNCHING)
			send_msg(sock, self.mtool.fill_msg('starting_experiment',
							sender=self.uuid))
			self.status_changed(self.status.status_name, self.status.details)
			result, details = self._start_experiment()
			if not result:
				send_msg(self._publish_socket, self.mtool.fill_msg("experiment_launch_error",
									 sender=self.uuid, err_code='', details=details))
				print self.name,'[', self.type, ']',  ':-('
				self.status.set_status(launcher_tools.FAILED_LAUNCH, details)
			self.status_changed(self.status.status_name, self.status.details)


	@msg_handlers.handler('join_experiment')
	def handle_join_experiment(self, message, sock):
		if message.peer_id in self.exp_config.peers or \
			message.peer_id in self.unsupervised_peers:
			send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
									err_code='peer_id_in_use'))

		elif self.status.status_name != launcher_tools.RUNNING:
			send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
									err_code='exp_status_'+self.status.status_name,
											details=self.status.details))
		else:
			self.unsupervised_peers[message.peer_id] = dict(peer_type=message.peer_type,
															path=message.path)
			send_msg(sock, self.mtool.fill_msg('rq_ok', params=dict(mx_addr=self.mx_addr)))

	@msg_handlers.handler('leave_experiment')
	def handle_leave_experiment(self, message, sock):
		if not message.peer_id in self.unsupervised_peers:
			send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
									err_code='peer_id_not_found'))
		else:
			del self.unsupervised_peers[message.peer_id]
			send_msg(sock, self.mtool.fill_msg('rq_ok'))

	@msg_handlers.handler("obci_peer_registered")
	def handle_obci_peer_registered(self, message, sock):
		peer_id = message.peer_id
		if not peer_id in self.exp_config.peers:
			print "{0} [{1}], Unknown Peer registered!!! {2}".format(
								self.name, self.peer_type(), peer_id)
		else:
			print "{0} [{1}], Peer registered!!! {2}".format(
								self.name, self.peer_type(),
								peer_id)
			for par, val in message.params.iteritems():
				self.exp_config.update_local_param(peer_id, par, val)
			send_msg(self._publish_socket, self.mtool.fill_msg('obci_control_message', 
										severity='info', msg_code='obci_peer_registered',
										launcher_message=message.dict(),
										sender=self.uuid, peer_name=self.name, peer_type=self.peer_type(),
										sender_ip=self.origin_machine))

	@msg_handlers.handler("obci_peer_params_changed")
	def handle_obci_peer_params_changed(self, message, sock):
		peer_id = message.peer_id
		if not peer_id in self.exp_config.peers:
			print "{0} [{1}], Unknown Peer update!!! {2}".format(
								self.name, self.peer_type(), peer_id)
		else:
			print "{0} [{1}], Params changed!!! {2} {3}".format(
								self.name, self.peer_type(), peer_id, message.params)
			for par, val in message.params.iteritems():
				try:
					self.exp_config.update_local_param(peer_id, par, val)
				except Exception, e:
					print "{0} [{1}], Invalid params!!! {2} {3} {4}".format(
								self.name, self.peer_type(), peer_id,
								message.params, str(e))

			send_msg(self._publish_socket, self.mtool.fill_msg('obci_control_message', 
										severity='info', msg_code='obci_peer_params_changed',
										launcher_message=message.dict(),
										sender=self.uuid, peer_name=self.name, peer_type=self.peer_type(),
										sender_ip=self.origin_machine))
			


	@msg_handlers.handler("obci_peer_ready")
	def handle_obci_peer_ready(self, message, sock):
		pass


# {"status": ["failed", null],
# "sender": "fb32da42-c8b6-47db-a958-249cd5e1f366",
# "receiver": "", "sender_ip": "127.0.0.1",
# "path": "/home/administrator/dev/openbci/acquisition/info_saver_peer.py",
# "peer_id": "info_saver", "type": "obci_peer_dead"}

	@msg_handlers.handler('obci_peer_dead')
	def handle_obci_peer_dead(self, message, sock):
		if not message.peer_id in self.exp_config.peers:
			print self.name, '[', self.type, ']', "peer_id ", message.peer_id, "not found."
			return
		status = message.status[0]
		details = message.status[1]

		self.status.peer_status(message.peer_id).set_status(status, details=details)
		if status == launcher_tools.FAILED:
			send_msg(self._publish_socket,
						self.mtool.fill_msg("stop_all", receiver=""))
			self.status.set_status(launcher_tools.FAILED,
									details='Failed process ' + message.peer_id)
		elif not self.status.peer_status_exists(launcher_tools.RUNNING) and\
				self.status.status_name != launcher_tools.FAILED:
			self.status.set_status(status)
		message.experiment_id = self.uuid
		send_msg(self._publish_socket, message.SerializeToString())
		self.status_changed(self.status.status_name, self.status.details)


	@msg_handlers.handler('update_peer_config')
	def handle_update_peer_config(self, message, sock):
		if self.status.status_name not in [launcher_tools.NOT_READY, \
										launcher_tools.READY_TO_LAUNCH]:
			send_msg(sock, self.mtool.fill_msg('rq_error', err_code='update_not_possible',
										details='Experiment status: '+self.status.status_name))
		else:
			conf = dict(local_params=message.local_params,
						external_params=message.external_params,
						launch_dependencies=message.launch_dependencies,
						config_sources=message.config_sources)
			peer_id = message.peer_id

			try:
				self.exp_config.update_peer_config(peer_id, conf)
			except Exception, e:
				send_msg(sock, self.mtool.fill_msg('rq_error', err_code='update_failed',
										details=str(e)))
			else:
				send_msg(sock, self.mtool.fill_msg('rq_ok'))



	@msg_handlers.handler('save_scenario')
	def handle_save_scenario(self, message, sock):
		send_msg(sock, self.mtool.fill_msg('rq_error', err_code='action_not_supported'))

	def cleanup_before_net_shutdown(self, kill_message, sock=None):
		send_msg(self._publish_socket,
						self.mtool.fill_msg("kill", receiver="", sender=self.uuid))
		print '{0} [{1}] -- sent KILL to supervisors'.format(self.name, self.peer_type())

	def clean_up(self):
		print self.name,'[', self.type, ']',  "exp cleaning up"
		self.subprocess_mgr.stop_monitoring()

	def _handle_register_sv_timeout(self, sv_process):
		txt = "Supervisor for machine {0} FAILED TO REGISTER before timeout".format(
																sv_process.machine_ip)
		print self.name,'[', self.type, ']', txt

		sock = self._push_sock(self.ctx, self._push_addr)

		# inform observers about failure
		send_msg(sock, self.mtool.fill_msg("experiment_launch_error",
												sender=self.uuid,
												err_code="create_supervisor_error",
												details=dict(machine=sv_process.machine_ip,
															error=txt)))
		sock.close()

	@msg_handlers.handler("get_tail")
	def handle_get_tail(self, message, sock):
		if self.status.status_name == launcher_tools.RUNNING:
			if not message.peer_id in self.exp_config.peers:
				send_msg(sock, self.mtool.fill_msg("rq_error",
											err_code="peer_not_found",
											details="No such peer: "+message.peer_id))
				return
			machine = self.exp_config.peer_machine(message.peer_id)
			print self.name,'[', self.type, ']', "getting tail for", message.peer_id, machine
			send_msg(self._publish_socket, message.SerializeToString())
			self.client_rq = (message, sock)

	@msg_handlers.handler("tail")
	def handle_tail(self, message, sock):
		if self.client_rq:
			if message.peer_id == self.client_rq[0].peer_id:
				send_msg(self.client_rq[1], message.SerializeToString())


def experiment_arg_parser():
	parser = argparse.ArgumentParser(parents=[basic_arg_parser()],
					description='Create, launch and manage an OBCI experiment.')
	parser.add_argument('--sv-pub-addresses', nargs='+',
					help='Addresses of the PUB socket of the supervisor')
	parser.add_argument('--sandbox-dir',
					help='Directory to store temporary and log files')
	parser.add_argument('--launch-file',
					help='Experiment launch file')
	parser.add_argument('--name', default='obci_experiment',
					help='Human readable name of this process')
	parser.add_argument('--launch', default=False,
	                   help='Launch the experiment specified in launch file')
	parser.add_argument('--ovr', nargs=argparse.REMAINDER)


	return parser

if __name__ == '__main__':

	args = experiment_arg_parser().parse_args()
	print args
	pack = None
	if args.ovr is not None:
		pack = peer_cmd.peer_overwrites_pack(args.ovr)
	exp = OBCIExperiment(args.obci_dir, args.sandbox_dir,
							args.launch_file, args.sv_addresses, args.sv_pub_addresses,
							args.rep_addresses, args.pub_addresses, args.name,
							args.launch, overwrites=pack)

	exp.run()
