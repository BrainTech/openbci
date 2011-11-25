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

import obci_experiment
import obci_process_supervisor

REGISTER_TIMEOUT = 3

class OBCIServer(OBCIControlPeer):
	def __init__(self, obci_install_dir, other_srv_addresses,
												rep_addresses=None,
												pub_addresses=None,
												name='obci_server'):
		self.other_addrs = other_srv_addresses
		self.experiments = {}
		self.exp_processes = {}

		self.worker_processes = {}



		self.__all_sockets = []

		super(OBCIServer, self).__init__(obci_install_dir, None, rep_addresses,
														  pub_addresses,
														  name)
		#TODO do sth with other server rep addresses

	def peer_type(self):
		return 'obci_server'

	def net_init(self):

		(self.exp_rep, self.exp_rep_addrs) = self._init_socket(
												None, zmq.REP)
		(self.exp_pub, self.exp_pub_addrs) = self._init_socket(
												None, zmq.PUB)
		super(OBCIServer, self).net_init()
		# (self.srv_rep, self.srv_addresses) = self._init_socket(
		# 										None, zmq.REP)
		# (self.srv_pub, self.srv_addresses) = self._init_socket(
		# 										None, zmq.PUB)


	def custom_sockets(self):
		return [self.exp_rep, self.exp_pub]#, self.srv_rep, self.srv_pub]

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


	def start_experiment_process(self, sandbox_dir, launch_file):
		path = obci_experiment.__file__
		path = '.'.join([path.rsplit('.', 1)[0], 'py'])

		args = ['python', path]
		args.append('--sv-addresses')
		args += self.exp_rep_addrs
		args.append('--sv-pub-addresses')
		args += self.exp_pub_addrs
		args += [
					'--obci-dir', self.obci_dir,
					'--sandbox-dir', str(sandbox_dir),
					'--launch-file', str(launch_file),
					'--name', os.path.basename(launch_file)]
		# try:
		exp = subprocess.Popen(args)

		# except OSError:
		# 	print "Unable to spawn experiment process!!!"
		#	return None
		# except ValueError:
		# 	print "Bad arguments!"
		return exp


	def handle_register_supervisor(self, message, sock):
		sv_uuid = message["uuid"]
		new_sv = self.supervisors[sv_uuid] = {}
		new_sv["rep_addrs"] = message["rep_addrs"]
		new_sv["pub_addrs"] = message["pub_addrs"]
		new_sv["name"] = message["name"]

		result = self.mtool.fill_msg("rq_ok")
		if message["main"]:
			if self.main_sv == None:
				self.main_sv = uuid
			else:
				result = self.mtool.fill_msg("rq_error",
					request=message, err_code="main_supervisor_already_exists")
		send_msg(sock, result)

	def handle_register_experiment(self, message, sock):
		print "REGISTER!!!! {0}".format(message.peer_type)

		info = self.experiments[message.uuid] = ExperimentInfo(message.uuid,
															message.name,
															message.rep_addrs,
															message.pub_addrs,
															time.time())

		if self.client_rq:
			msg_type = self.client_rq[0].type
			rq_sock = self.client_rq[1]
			if msg_type == "create_experiment":
				self.client_rq = None

				send_msg(rq_sock, self.mtool.fill_msg("experiment_created",
												uuid=info.uuid,
												name=info.name,
												rep_addrs=info.rep_addrs,
												pub_addrs=info.pub_addrs))
			self.exp_timer.cancel()

		send_msg(sock, self.mtool.fill_msg("rq_ok"))

	def handle_register_experiment_timeout(self, exp):
		if exp.returncode is None:
			exp.kill()

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
		print "CREATE EXP!!! {0}".format(message.launch_file)
		launch_file = message.launch_file
		sandbox = message.sandbox_dir

		sandbox = sandbox if sandbox else settings.DEFAULT_SANDBOX_DIR

		exp = self.start_experiment_process(sandbox, launch_file)
		if exp is None:
			send_msg(sock, self.mtool.fill_msg("rq_error", request=vars(message),
								err_code='launch_error'))
		else:
			self.exp_processes[exp.pid] = exp
			# now wait for experiment to register itself here
			self.client_rq = (message, sock)
			self.exp_timer = threading.Timer(REGISTER_TIMEOUT,
										self.handle_register_experiment_timeout,
										[exp])
			self.exp_timer.start()

	def handle_list_experiments(self, message, sock):
		exp_data = {}
		for exp_id in self.experiments:
			exp_data[exp_id] = self.experiments[exp_id].info()

		send_msg(sock, self.mtool.fill_msg("running_experiments",
												exp_data=exp_data))






class ExperimentInfo(object):
	def __init__(self, uuid, name, rep_addrs, pub_addrs, registration_time):
		self.uuid = uuid
		self.name = name
		self.rep_addrs = rep_addrs
		self.pub_addrs = pub_addrs
		self.registration_time = registration_time

	def info(self):
		return vars(self)


def server_arg_parser(add_help=False):
	parser = argparse.ArgumentParser(parents=[basic_arg_parser()],
							description="OBCI Server : manage OBCI experiments.",
							add_help=add_help)
	parser.add_argument('--other-srv-addresses', nargs='+',
	                   help='REP Addresses of OBCI servers on other machines')
	parser.add_argument('--name', default='obci_server',
	                   help='Human readable name of this process')
	return parser


if __name__ == '__main__':
	parser = server_arg_parser(add_help=True)

	args = parser.parse_args()

	srv = OBCIServer(args.obci_dir, args.other_srv_addresses,
							args.rep_addresses, args.pub_addresses, args.name)
	srv.run()