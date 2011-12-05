#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import threading
import uuid
import argparse
import os.path
import sys
import json
import time

import zmq

from common.message import OBCIMessageTool, send_msg, recv_msg
from launcher_messages import message_templates, error_codes

from obci_control_peer import OBCIControlPeer, basic_arg_parser
import common.obci_control_settings as settings
import common.net_tools as net

import obci_experiment
import obci_process_supervisor
import subprocess_monitor
from subprocess_monitor import SubprocessManager, TimeoutDescription,\
STDIN, STDOUT, STDERR, NO_STDIO

REGISTER_TIMEOUT = 3

class OBCIServer(OBCIControlPeer):
	def __init__(self, obci_install_dir, other_srv_ips,
												rep_addresses=None,
												pub_addresses=None,
												name='obci_server'):
		self.other_addrs = other_srv_ips

		self.experiments = {}
		self.exp_processes = {}

		self.exp_process_supervisors = {}

		self.machine = net.ext_ip()

		self.__all_sockets = []

		super(OBCIServer, self).__init__(obci_install_dir, None, rep_addresses,
														  pub_addresses,
														  name)
		self.subprocess_mgr = SubprocessManager(self.ctx, self.uuid)
		#TODO do sth with other server rep addresses

	def peer_type(self):
		return 'obci_server'

	def net_init(self):

		(self.exp_rep, self.exp_rep_addrs) = self._init_socket(
												['ipc://rep_server_exp.ipc'], zmq.REP)
		(self.exp_pub, self.exp_pub_addrs) = self._init_socket(
												['ipc://pub_server_exp.ipc'], zmq.PUB)
		super(OBCIServer, self).net_init()
		# (self.srv_rep, self.srv_addresses) = self._init_socket(
		# 										None, zmq.REP)
		# (self.srv_pub, self.srv_addresses) = self._init_socket(
		# 										None, zmq.PUB)


	def custom_sockets(self):
		return [self.exp_rep]#, self.srv_rep, self.srv_pub]

	def pre_run(self):
		"""
		Subclassed from OBCIControlPeer. Create a file in temp directory with
		REP addresses.
		"""
		directory = os.path.abspath(settings.DEFAULT_SANDBOX_DIR)
		if not os.path.exists(directory):
			os.mkdir(directory)

		filename = settings.SERVER_CONTACT_NAME
		self.fpath = os.path.join(directory, filename)
		if os.path.exists(self.fpath):
			print "\nOBCIServer contact file exists, \
probably a server is already working"
			print "Abort.\n"
			sys.exit(2)

		with open(self.fpath, 'w') as f:
			f.write(str(os.getpid()))
			#json.dump(self.rep_addresses, f)


	def clean_up(self):
		# send "die" to everybody
		os.remove(self.fpath)

	def _args_for_experiment(self, sandbox_dir, launch_file, local=False):

		args = ['--sv-addresses']
		args += self.exp_rep_addrs
		args.append('--sv-pub-addresses')
		if local:
			addrs = [pub for pub in self.exp_pub_addrs if pub.startswith('ipc://')]
		else:
			addrs = [pub for pub in self.exp_pub_addrs if pub.startswith('tcp://')]
		args += [addrs.pop()]
		args += [
					'--obci-dir', self.obci_dir,
					'--sandbox-dir', str(sandbox_dir),
					'--launch-file', str(launch_file),
					'--name', os.path.basename(launch_file)]
		return args

	def start_experiment_process(self, sandbox_dir, launch_file):
		path = obci_experiment.__file__
		path = '.'.join([path.rsplit('.', 1)[0], 'py'])

		args = ['python', path]
		args += self._args_for_experiment(sandbox_dir, launch_file, local=True)

		result, details, sv, exp_timer = False, None, None, None
		try:
			exp = subprocess.Popen(args)
		except OSError as e:
			details = e.args
			print "Unable to spawn experiment!!!"
		except ValueError as e:
			details = e.args
			print "Bad arguments!"
		else:
			result = True
			reg_timer = threading.Timer(REGISTER_TIMEOUT,
										self._handle_register_experiment_timeout,
										[exp])
			reg_timer.start()

		return result, details, exp, reg_timer


	def handle_register_experiment(self, message, sock):
		info = self.experiments[message.uuid] = ExperimentInfo(message.uuid,
															message.name,
															message.rep_addrs,
															message.pub_addrs,
															time.time(),
															message.other_params['origin_machine'],
															message.other_params['pid'])

		if self.client_rq:
			msg_type = self.client_rq[0].type
			rq_sock = self.client_rq[1]
			if msg_type == "create_experiment":
				timer = self.client_rq[2]
				self.client_rq = None
				timer.cancel()
				send_msg(rq_sock, self.mtool.fill_msg("experiment_created",
												uuid=info.uuid,
												name=info.name,
												rep_addrs=info.rep_addrs,
												pub_addrs=info.pub_addrs,
												machine=info.origin_machine))


		send_msg(sock, self.mtool.fill_msg("rq_ok"))

	def _handle_register_experiment_timeout(self, exp):
		print """New experiment process failed to register before timeout""", exp
		pid = exp.pid
		if exp.returncode is None:
			exp.kill()
		del self.exp_processes[pid]

		msg_type = self.client_rq[0].type
		rq_sock = self.client_rq[1]
		send_msg(rq_sock, self.mtool.fill_msg("rq_error",
												err_code="create_experiment_error",
												request=vars(self.client_rq[0])))

	def handle_register_peer(self, message, sock):
		if message.peer_type == "obci_client":
			send_msg(sock, self.mtool.fill_msg("rq_ok"))
		elif message.peer_type == "obci_experiment":
			self.handle_register_experiment(message, sock)
		else:
			super(OBCIServer, self).handle_register_peer(message, sock)

	def handle_create_experiment(self, message, sock):
		#print "CREATE EXP!!! {0}".format(message.launch_file)
		launch_file = message.launch_file
		sandbox = message.sandbox_dir

		sandbox = sandbox if sandbox else settings.DEFAULT_SANDBOX_DIR

		result, details, exp, reg_timer = \
							self.start_experiment_process(sandbox, launch_file)

		if result is False:
			send_msg(sock, self.mtool.fill_msg("rq_error", request=vars(message),
								err_code='launch_error', details=details))
		else:
			self.exp_processes[exp.pid] = exp
			# now wait for experiment to register itself here
			self.client_rq = (message, sock, reg_timer)


	def handle_list_experiments(self, message, sock):
		exp_data = {}
		for exp_id in self.experiments:
			exp_data[exp_id] = self.experiments[exp_id].info()

		send_msg(sock, self.mtool.fill_msg("running_experiments",
												exp_data=exp_data))

	def _handle_match_name(self, message, sock, this_machine=False):
		matches = self.exp_matching(message.strname)
		match = None
		msg = None
		if not matches:
			msg = self.mtool.fill_msg("rq_error", request=vars(message),
							err_code='experiment_not_found')

		elif len(matches) > 1:
			matches = [(exp.uuid, exp.name) for exp in matches]
			msg = self.mtool.fill_msg("rq_error", request=vars(message),
							err_code='ambiguous_exp_name',
							details=matches)
		else:
			match = matches.pop()
			if this_machine and match.origin_machine != self.machine:
				msg = self.mtool.fill_msg("rq_error", request=vars(message),
							err_code='exp_not_on_this_machine', details=match.origin_machine)
				match = None
		if msg and sock.socket_type in [zmq.REP, zmq.ROUTER]:
			send_msg(sock, msg)
		return match

	def handle_get_experiment_contact(self, message, sock):
		print "##### rq contact for: ", message.strname

		info = self._handle_match_name(message, sock)
		if info:
			send_msg(sock, self.mtool.fill_msg("experiment_contact",
												uuid=info.uuid,
												name=info.name,
												rep_addrs=info.rep_addrs,
												pub_addrs=info.pub_addrs,
												machine=info.origin_machine))


	def exp_matching(self, strname):
		"""Match *strname* against all created experiment IDs and
		names. Return those experiment descriptions which name
		or uuid starts with strname.
		"""
		match_names = {}
		for uid, exp in self.experiments.iteritems():
			if exp.name.startswith(strname):
				match_names[uid] = exp

		ids = self.experiments.keys()
		match_ids = [uid for uid in ids if uid.startswith(strname)]

		experiments = set()
		for uid in match_ids:
			experiments.add(self.experiments[uid])
		for name, exp in match_names.iteritems():
			experiments.add(exp)

		return experiments

	def handle_kill_experiment(self, message, sock):
		match = self._handle_match_name(message, sock, this_machine=True)

		if match:

			if not message.force:
				print "{0} [{1}] - sending kill to experiment {2} ({3})".format(
									self.name, self.peer_type(),match.uuid, match.name)
				send_msg(self.exp_pub,
						self.mtool.fill_msg("kill", receiver=match.uuid))

				send_msg(sock, self.mtool.fill_msg("kill_sent"))
				pid = match.experiment_pid
				uid = match.uuid
				match.kill_timer = threading.Thread(
									target=self._handle_killing_exp, args=[pid, uid])
				match.kill_timer.start()
				#match.kill_timer = threading.Timer(REGISTER_TIMEOUT,
				#						self._handle_kill_experiment_timeout,
				#						[match])

	def _handle_killing_exp(self, pid, uid):
		print "Waiting for experiment process {0} to terminate".format(uid)

		if pid in self.exp_processes:
			popen_obj = self.exp_processes[pid]

			returncode = popen_obj.wait()
			print "{0} [{1}] - experiment {2} FINISHED".format(
									self.name, self.peer_type(), uid)

			del self.exp_processes[pid]
			if uid in self.experiments:
				del self.experiments[uid]
			return returncode

	def handle_launch_process(self, message, sock):
		if message.proc_type == 'obci_process_supervisor':
			self._handle_launch_process_supervisor(message, sock)

	def _handle_launch_process_supervisor(self, message, sock):
		sv_obj, details = self._start_obci_supervisor_process( message)
		self.exp_process_supervisors[message.sender] = sv_obj

		if sv_obj:
			send_msg(sock,
					self.mtool.fill_msg("launched_process_info",
											sender=self.uuid, machine=self.machine,
											pid=sv_obj.pid, proc_type=sv_obj.proc_type,
											name=sv_obj.name,
											path=sv_obj.path))
		else:
			send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
												err_code="launch_error",
												details=details))

	def handle_kill_process_supervisor(self, message, sock):
		proc = self.exp_process_supervisors.get(message.sender, None)
		if not proc:
			send_msg(sock, self.mtool.fill_msg("rq_error", err_code="experiment_not_found"))
		else:
			proc.kill()
			proc.popen_obj.wait()
			send_msg(sock, self.mtool.fill_msg("rq_ok"))
			del self.exp_process_supervisors[message.sender]


	def _start_obci_supervisor_process(self, rq_message):
		path = obci_process_supervisor.__file__
		path = '.'.join([path.rsplit('.', 1)[0], 'py'])
		start_params = rq_message.dict()
		start_params['path'] = path
		del start_params['type']
		del start_params['sender']
		del start_params['receiver']
		sv_obj, details = self.subprocess_mgr.new_local_process(**start_params)
		if sv_obj is None:
			return False, details

		return sv_obj, False

	def _join_srv_network(self, srv_address):
		# send srv_table_request
		# update sekf's srv
		# send announce_request
		#
		pass


class ExperimentInfo(object):
	def __init__(self, uuid, name, rep_addrs, pub_addrs, registration_time,
							origin_machine, pid):
		self.uuid = uuid
		self.name = name
		self.rep_addrs = rep_addrs
		self.pub_addrs = pub_addrs
		self.registration_time = registration_time
		self.origin_machine = origin_machine
		self.experiment_pid = pid
		self.kill_timer = None

	def from_dict(dic):
		try:
			return ExperimentInfo(dic['uuid'], dic['rep_addrs'], dic['pub_addrs'],
					dic['registration_time'], dic['origin_machine'], dic['pid']), None
		except KeyError as e:
			return None, e.args

	def info(self):
		d = dict(uuid=self.uuid,
				name=self.name,
				rep_addrs=self.rep_addrs,
				pub_addrs=self.pub_addrs,
				registration_time=self.registration_time,
				origin_machine=self.origin_machine,
				experiment_pid=self.experiment_pid)

		return d


def server_arg_parser(add_help=False):
	parser = argparse.ArgumentParser(parents=[basic_arg_parser()],
							description="OBCI Server : manage OBCI experiments.",
							add_help=add_help)
	parser.add_argument('--other-srv-ips', nargs='+',
	                   help='IP addresses of OBCI servers on other machines')
	parser.add_argument('--name', default='obci_server',
	                   help='Human readable name of this process')
	return parser


if __name__ == '__main__':
	parser = server_arg_parser(add_help=True)

	args = parser.parse_args()

	srv = OBCIServer(args.obci_dir, args.other_srv_ips,
							args.rep_addresses, args.pub_addresses, args.name)
	srv.run()