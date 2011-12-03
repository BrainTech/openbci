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
		self.sv_processes = {} # pid -> (supervisro Popen object, timer)

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

	def args_for_process_sv(self, local=False):
		args = ['--sv-addresses']
		args += self.supervisors_rep_addrs
		args.append('--sv-pub-addresses')
		if local:
			addrs = [pub for pub in self.pub_addresses if pub.startswith('ipc://')]
		else:
			addrs = [pub for pub in self.pub_addresses if pub.startswith('tcp://')]
		args += [addrs.pop()] #self.pub_addresses
		args += [
					'--obci-dir', self.obci_dir,
					'--sandbox-dir', str(self.sandbox_dir),
					'--name', os.path.basename(
							self.launch_file + '-' + self.origin_machine)]
		return args

	def _start_obci_supervisor_process(self, args_for_proc_supervisor):
		path = obci_process_supervisor.__file__
		path = '.'.join([path.rsplit('.', 1)[0], 'py'])

		args = ['python', path]
		args += args_for_proc_supervisor

		result, details, sv, reg_timer = False, None, None, None
		try:
			sv = subprocess.Popen(args)
		except OSError as e:
			details = e.args
			print "Unable to spawn process supervisor!!!"
		except ValueError as e:
			details = e.args
			print "Bad arguments!"
		else:
			result = True
			reg_timer = threading.Timer(REGISTER_TIMEOUT,
										self._handle_register_sv_timeout,
										[sv, self.origin_machine])
			reg_timer.start()

		return result, details, sv, reg_timer


	def _request_supervisor(self, machine_addr):
		result, details, response, reg_timer = None, None, None, None
		return result, details, response, reg_timer

	def _handle_register_sv_timeout(self, sv_popen, machine):
		print "Supervisor for machine {0} FAILED TO REGISTER before timeout".format(machine)
		if machine == self.origin_machine and sv_popen is not None:
			pid = sv_popen.pid
			if sv_popen.returncode is None:
				sv_popen.kill()
				sv_popen.wait()
			del self.sv_processes[pid]
		else:
			# send KILL request for the rogue supervisor
			pass

		msg_type = self.start_rq[0].type
		rq_sock = self.start_rq[1]
		send_msg(rq_sock, self.mtool.fill_msg("rq_error",
												err_code="create_supervisor_error",
												request=vars(self.start_rq[0])))

	def _start_experiment(self, message, sock):
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

		result, details, sv_popen, reg_timer = \
							self._start_obci_supervisor_process(
									self._args_for_proc_supervisor(local=True))

		if result is False:
			return False, self.mtool.fill_msg("rq_error", request=vars(message),
								err_code='launch_supervisor_os_error', details=details)
		else:
			self.sv_processes[sv_popen.pid] = sv_popen
			# now wait for experiment to register itself here
			self.start_rq = (message, sock, reg_timer)
			return True,
		pass

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
			desc = self.supervisors[message.other_params['machine']] = \
							ProcessSupervisorDescription(
												message.uuid,
												message.name,
												message.rep_addrs,
												message.pub_addrs,
												message.other_params['machine'],
												message.other_params['pid'])
			self.start_rq[2].cancel()
			# subscribe to sv pub
			send_msg(self.start_rq[1], self.mtool.fill_msg('starting_experiment',
															sender=self.uuid))
			send_msg(sock, self.mtool.fill_msg("rq_ok"))


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
			result, msg = self._start_experiment(message, sock)



	def cleanup_before_net_shutdown(self, kill_message, sock=None):
		send_msg(self.pub_socket,
						self.mtool.fill_msg("kill", receiver=""))
		print '{0} [{1}] -- sent KILL to supervisors'.format(self.name, self.peer_type())


class ProcessSupervisorDescription(object):
	def __init__(self, uuid, name, rep_addrs, pub_addrs, machine, pid):
		self.machine = machine
		self.pid = pid
		self.uuid = uuid
		self.name = name
		self.rep_addrs = rep_addrs
		self.pub_addrs = pub_addrs

	def info(self):
		return vars(self).copy()


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
