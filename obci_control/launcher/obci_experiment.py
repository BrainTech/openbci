#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import uuid
import argparse
import subprocess
import threading

import zmq

from common.message import OBCIMessageTool, send_msg, recv_msg
from launcher_messages import message_templates
import common.net_tools as net
import common.obci_control_settings as settings

from obci_control_peer import OBCIControlPeer, basic_arg_parser
from subprocess_monitor import SubprocessManager, TimeoutDescription,\
STDIN, STDOUT, STDERR, NO_STDIO
from obci_control_peer import RegistrationDescription
import subprocess_monitor

import launch_file_parser
import launcher_tools
import system_config
import obci_process_supervisor

REGISTER_TIMEOUT = 15

class OBCIExperiment(OBCIControlPeer):

	def __init__(self, obci_install_dir, sandbox_dir, launch_file=None,
										source_addresses=None,
										source_pub_addresses=None,
										rep_addresses=None,
										pub_addresses=None,
										name='obci_experiment',
										launch=False):

		###TODO TODO TODO !!!!
		###cleaner subclassing of obci_control_peer!!!
		self.source_pub_addresses = source_pub_addresses
		self.origin_machine = net.ext_ip()
		super(OBCIExperiment, self).__init__(obci_install_dir,
											source_addresses,
											rep_addresses,
											pub_addresses,
											name)
		self.sandbox_dir = sandbox_dir if sandbox_dir else settings.DEFAULT_SANDBOX_DIR

		self.launch_file = launch_file
		self.supervisors = {} #machine -> supervisor contact/other info
		self._wait_register = 0
		self.sv_processes = {} # machine -> Process objects)
		self.subprocess_mgr = SubprocessManager(self.ctx, self.uuid)

		self.status = launcher_tools.ExperimentStatus()

		self.exp_config = system_config.OBCIExperimentConfig(uuid=self.uuid)
		self.exp_config.origin_machine = self.origin_machine
		self.exp_config.launch_file_path = self.launch_file

		result, details = self.make_experiment_config()

		if not result and self.launch_file:
			print "LAUNCH FILE INVALID"

		self.exp_config.status(self.status)
		self.status.details = details



	def net_init(self):
		self.source_sub_socket = self.ctx.socket(zmq.SUB)
		self.source_sub_socket.setsockopt(zmq.SUBSCRIBE, "")
		if self.source_pub_addresses:
			for addr in self.source_pub_addresses:
				self.source_sub_socket.connect(addr)

		(self.supervisors_rep, self.supervisors_rep_addrs) = self._init_socket(
									['ipc://rep_experiment_supervisors-'+self.uuid +'.ipc'],
									zmq.REP)
		(self.supervisors_sub, self.supervisors_sub_addrs) = (self.ctx.socket(zmq.SUB), [])

		super(OBCIExperiment, self).net_init()

	def params_for_registration(self):
		return dict(pid=os.getpid(), origin_machine=self.origin_machine)

	def custom_sockets(self):
		return [self.source_sub_socket, self.supervisors_sub, self.supervisors_rep]

	def args_for_process_sv(self, machine, local=False):
		args = ['--sv-addresses']
		args += self.supervisors_rep_addrs
		args.append('--sv-pub-addresses')
		if local:
			addrs = net.choose_local(self.pub_addresses)
		else:
			addrs = net.choose_not_local(self.pub_addresses)

		args += [addrs.pop()] #self.pub_addresses
		args += [
					'--obci-dir', self.obci_dir,
					'--sandbox-dir', str(self.sandbox_dir),
					'--name', 'sv-' + os.path.basename(self.launch_file) +\
							 '-' + self.uuid.split('-',1)[0] + \
							'-' + machine]
		return args

	def _start_obci_supervisor_process(self, args_for_proc_supervisor):
		path = obci_process_supervisor.__file__
		path = '.'.join([path.rsplit('.', 1)[0], 'py'])

		args = args_for_proc_supervisor

		sv_obj, details = self.subprocess_mgr.new_local_process(path, args,
												proc_type='obci_process_supervisor',
													capture_io=NO_STDIO)
		if sv_obj is None:
			return False, details

		timeout_handler = TimeoutDescription(timeout=REGISTER_TIMEOUT,
						timeout_method=self._handle_register_sv_timeout,
						timeout_args=(sv_obj))
		sv_obj.set_registration_timeout_handler(timeout_handler)
		self.sv_processes[self.origin_machine] = sv_obj

		return sv_obj, None

	def _request_supervisor(self, machine_addr):
		args = self.args_for_process_sv(machine_addr)
		proc_type = 'obci_process_supervisor'
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
						timeout_args=(sv_obj))
		sv_obj.set_registration_timeout_handler(timeout_handler)
		self.sv_processes[machine_addr] = sv_obj
		return sv_obj, None

	def _handle_register_sv_timeout(self, sv_process):
		txt = "Supervisor for machine {0} FAILED TO REGISTER before timeout".format(
																sv_process.machine_ip)
		print txt

		if sv_process.machine_ip == self.origin_machine and sv_process.is_local():
			pid = sv_process.pid
			if sv_process.popen_obj.returncode is None:
				sv_process.kill()
				sv_process.popen_obj.wait()
			del self.sv_processes[sv_process.machine_ip]
		else:
			# send KILL request for the rogue supervisor
			pass
		self._wait_register = 0

		# inform observers about failure
		send_msg(self.pub_socket, self.mtool.fill_msg("experiment_launch_error",
												sender=self.uuid,
												err_code="create_supervisor_error",
												details=dict(machine=sv_process.machine_ip,
															error=txt)))

	def _start_experiment(self):
		# * check status - if != READY_TO_LAUNCH - error
		# * start supervisor on origin machine (here)
		# *  --for every other machine send request for a supervisor
		# * wait until all supervisors register
		#				if timeout then error
		# * if mx, send mx start request for main supervisor
		# * send peer paths and configs to respective machine supervisors
		# * send START signal
		# * gather start reports from all supervisors
		# * if all processes started and didn't manage to crash before report,
		#		# ok, status = running
		# * if something crashed, then shutdown everything
		#       # error, status = crashed
		#        ---> send result to the requesting client
		#print "CREATE EXP!!! {0}".format(message.launch_file)

		result, details = \
							self._start_obci_supervisor_process(
									self.args_for_process_sv(self.origin_machine, local=True))
		self._wait_register = len(self.exp_config.peer_machines())

		if not result:
			#return False, self.mtool.fill_msg("rq_error", request=vars(message),
			#					err_code='launch_supervisor_os_error', details=details)
			print "FAILED to start local supervisor", details
			self.status.set_status(launcher_tools.CRASHED, details)
			return False, details
		else:
			for machine in self.exp_config.peer_machines():
				print "^^^^^^^^    ", machine
				if machine == self.origin_machine:
					pass

				result, details = self._request_supervisor(machine)
				if not result:
					return False, details

			#k = ':'.join[result.machine_ip, result.pid]
			k = result.machine_ip
			self.sv_processes[k] = result
			# now wait for experiment to register itself here
			return True, details


	def _start_all_supervisors(self):
		for machine in self.exp_config.peer_machines():
			result, details, response, req_timer = self._request_supervisor(machine)


	def make_experiment_config(self):
		launch_parser = launch_file_parser.LaunchFileParser(launcher_tools.obci_root())
		try:
			with open(self.launch_file) as f:
				launch_parser.parse(f, self.exp_config)
		except Exception as e:
			self.status.set_status(launcher_tools.NOT_READY, details=e.args)
			return False, e.args

		#print self.exp_config
		if self.exp_config.config_ready():
			self.status.set_status(launcher_tools.READY_TO_LAUNCH)
		return True, None

	def peer_type(self):
		return 'obci_experiment'

	def handle_register_peer(self, message, sock):
		if message.peer_type == "obci_process_supervisor":
			if self._wait_register > 0:
				self._wait_register -= 1
			else:
				send_msg(sock, self.mtool.fill_msg("rq_error",
								err_code='peer_spam', request=message.dict()))
				return

			desc = self.supervisors[message.other_params['machine']] = \
							RegistrationDescription(
												message.uuid,
												message.name,
												message.rep_addrs,
												message.pub_addrs,
												message.other_params['machine'],
												message.other_params['pid'])
			print self.sv_processes
			proc = self.sv_processes[desc.machine]
			proc.registered(desc)
			addrs = []
			if proc.is_local():
				addrs = net.choose_local(desc.pub_addrs)
			if not addrs:
				addrs = net.choose_not_local(desc_pub_addrs)
			if addrs:
				a = addrs.pop()
				self.supervisors_sub_addrs.append(a)
				self.supervisors_sub.connect(a)

			send_msg(sock, self.mtool.fill_msg("rq_ok"))

			# inform observers
			send_msg(self.pub_socket, self.mtool.fill_msg("process_supervisor_registered",
												sender=self.uuid,
												machine_ip=desc.machine))


	def handle_get_experiment_info(self, message, sock):
		## a not-launched version
		if message.peer_id:
			if message.peer_id not in self.exp_config.peers:
				send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
							err_code='peer_id_not_found'))
			else:
				exp_info = self.exp_config.peers[message.peer_id].info(detailed=True)
		else:
			exp_info = self.exp_config.info()
			exp_info['experiment_status'] = self.status.as_dict()

		#send_msg(self.pub_socket, self.mtool.fill_msg('ping', sender=self.uuid))
		send_msg(sock, self.mtool.fill_msg('experiment_info',
											exp_info=exp_info))

	def handle_get_peer_config(self, message, sock):
		send_msg(sock, self.mtool.fill_msg('ping', sender=self.uuid))


	def handle_start_experiment(self, message, sock):
		if not self.status.status_name == launcher_tools.READY_TO_LAUNCH:
			send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
											err_code='exp_status_'+self.status.status_name,
											details=self.status.details))
		else:
			self.status.set_status(launcher_tools.LAUNCHING)
			send_msg(sock, self.mtool.fill_msg('starting_experiment',
							sender=self.uuid))
			result, details = self._start_experiment()
			if not result:
				print "!!!!!!!!!!!!!!!!!!"
				send_msg(self.pub_socket, self.mtool.fill_msg("experiment_launch_error",
									 sender=self.uuid, err_code='', details=details))
				print "????????????"
				send_msg(self.pub_socket, self.mtool.fill_msg("experiment_launch_error",
									 sender=self.uuid, err_code='', details=details))
				send_msg(self.pub_socket, self.mtool.fill_msg("experiment_launch_error",
									 sender=self.uuid, err_code='', details=details))
				send_msg(self.pub_socket, self.mtool.fill_msg("experiment_launch_error",
									 sender=self.uuid, err_code='', details=details))
				print ':-('



	def cleanup_before_net_shutdown(self, kill_message, sock=None):
		send_msg(self.pub_socket,
						self.mtool.fill_msg("kill", receiver=""))
		print '{0} [{1}] -- sent KILL to supervisors'.format(self.name, self.peer_type())



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


	return parser

if __name__ == '__main__':



	args = experiment_arg_parser().parse_args()
	#print vars(args)

#	exp = OBCIExperiment( ['tcp://*:22233'], '/host/dev/openbci',
#							'~/.obci', None, 'obci_exp')
	exp = OBCIExperiment(args.obci_dir, args.sandbox_dir,
							args.launch_file, args.sv_addresses, args.sv_pub_addresses,
							args.rep_addresses, args.pub_addresses, args.name,
							args.launch)


	exp.run()
