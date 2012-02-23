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
from launcher_tools import module_path
from eeg_experiment_finder import find_eeg_experiments_and_push_results

from obci_control_peer import OBCIControlPeer, basic_arg_parser
import common.obci_control_settings as settings
import common.net_tools as net
from peer import peer_cmd

import obci_experiment
import obci_process_supervisor
import subprocess_monitor
from subprocess_monitor import SubprocessMonitor, TimeoutDescription,\
STDIN, STDOUT, STDERR, NO_STDIO

from server_scanner import update_nearby_servers, broadcast_server

REGISTER_TIMEOUT = 6

class OBCIServer(OBCIControlPeer):

	msg_handlers = OBCIControlPeer.msg_handlers.copy()

	def __init__(self, 	rep_addresses=None, pub_addresses=None, name='obci_server'):

		self.experiments = {}
		self.exp_process_supervisors = {}

		super(OBCIServer, self).__init__( None, rep_addresses,
														  pub_addresses,
														  name)
		self.machine = self.hostname
		self.subprocess_mgr = SubprocessMonitor(self.ctx, self.uuid)

		rep_port = int(net.server_rep_port())
		pub_port = int(net.server_pub_port())
		bcast_port = int(net.server_bcast_port())

		self._bcast_server = threading.Thread(target=broadcast_server,
												args=[self.uuid,
													rep_port, pub_port, bcast_port])
		self._bcast_server.daemon = True
		self._bcast_server.start()

		self._nearby_servers = {}
		self._nearby_servers_lock = threading.RLock()
		self._nearby_updater = threading.Thread(target=update_nearby_servers,
												args=[self._nearby_servers,
														self._nearby_servers_lock,
														bcast_port,
														self.ctx])

		self._nearby_updater.daemon = True
		self._nearby_updater.start()


	def nearby_server_addrs(self):
		with self._nearby_servers_lock:
			return dict(self._nearby_servers)

	def set_nearby_server_addrs(self, addr_list):
		with self._nearby_servers_lock:
			self._nearby_servers = list(addr_list)

	def peer_type(self):
		return 'obci_server'


	def net_init(self):

		(self.exp_rep, self.exp_rep_addrs) = self._init_socket(
												[], zmq.REP)
		(self.exp_pub, self.exp_pub_addrs) = self._init_socket(
												[], zmq.PUB)
		self.exp_pub.setsockopt(zmq.LINGER, 0)
		self._all_sockets.append(self.exp_rep)
		self._all_sockets.append(self.exp_pub)
		super(OBCIServer, self).net_init()


	def custom_sockets(self):
		return [self.exp_rep]#, self.srv_rep, self.srv_pub]

	def clean_up(self):
		pass

	def cleanup_before_net_shutdown(self, kill_message, sock=None):
		send_msg(self.exp_pub,
						self.mtool.fill_msg("kill", receiver=""))
		send_msg(self._publish_socket, self.mtool.fill_msg("launcher_shutdown",
						sender=self.uuid))
		print '{0} [{1}] -- sent KILL to experiments'.format(self.name, self.peer_type())


	def _args_for_experiment(self, sandbox_dir, launch_file, local=False, name=None, overwrites=None):

		args = ['--sv-addresses']
		args += self.exp_rep_addrs
		args.append('--sv-pub-addresses')
		# if local:
		# 	addrs = net.choose_local(self.exp_pub_addrs)
		# else:
		# 	addrs = net.choose_not_local(self.exp_pub_addrs)
		addrs = self.exp_pub_addrs

		args += addrs
		exp_name = name if name else os.path.basename(launch_file)
		args += [
					'--sandbox-dir', str(sandbox_dir),
					'--launch-file', str(launch_file),
					'--name', exp_name]
		if overwrites is not None:
			args += peer_cmd.peer_overwrites_cmd(overwrites)
		# print '{0} [{1}] -- experiment args: {2}'.format(self.name, self.peer_type(), args)
		return args

	def start_experiment_process(self, sandbox_dir, launch_file, name=None, overwrites=None):
		path = module_path(obci_experiment)

		args = self._args_for_experiment(sandbox_dir, launch_file, 
										local=True, name=name, overwrites=overwrites)

		return self.subprocess_mgr.new_local_process(path, args,
											proc_type='obci_experiment',
											capture_io=NO_STDIO)



	def handle_register_experiment(self, message, sock):
		machine, pid = message.other_params['origin_machine'], message.other_params['pid']
		status, det = message.other_params['status_name'], message.other_params['details']
		launch_file = message.other_params['launch_file_path']

		exp_proc = self.subprocess_mgr.process(machine, pid)

		if exp_proc is None:
			send_msg(sock, self.mtool.fill_msg("rq_error", err_code="experiment_not_found"))
			return

		info = self.experiments[message.uuid] = ExperimentInfo(message.uuid,
															message.name,
															message.rep_addrs,
															message.pub_addrs,
															time.time(),
															machine,
															pid,
															status,
															det,
															launch_file)

		exp_proc.registered(info)

		info_msg = self.mtool.fill_msg("experiment_created",
												uuid=info.uuid,
												name=info.name,
												rep_addrs=info.rep_addrs,
												pub_addrs=info.pub_addrs,
												origin_machine=info.origin_machine,
												status_name=status,
												details=det,
												launch_file_path=launch_file)

		if self.client_rq:
			msg_type = self.client_rq[0].type
			rq_sock = self.client_rq[1]
			if msg_type == "create_experiment":
				self.client_rq = None
				send_msg(rq_sock, info_msg)

		send_msg(sock, self.mtool.fill_msg("rq_ok"))
		send_msg(self._publish_socket, info_msg)

	def _handle_register_experiment_timeout(self, exp):
		print """New experiment process failed to register before timeout""", exp
		pid = exp.pid
		if exp.returncode is None:
			exp.kill()
			exp.wait()

		msg_type = self.client_rq[0].type
		rq_sock = self.client_rq[1]
		send_msg(rq_sock, self.mtool.fill_msg("rq_error",
												err_code="create_experiment_error",
												request=vars(self.client_rq[0])))


	@msg_handlers.handler("register_peer")
	def handle_register_peer(self, message, sock):
		"""Register peer"""
		if message.peer_type == "obci_client":
			send_msg(sock, self.mtool.fill_msg("rq_ok"))
		elif message.peer_type == "obci_experiment":
			self.handle_register_experiment(message, sock)
		else:
			super(OBCIServer, self).handle_register_peer(message, sock)


	@msg_handlers.handler("create_experiment")
	def handle_create_experiment(self, message, sock):

		launch_file = message.launch_file
		sandbox = message.sandbox_dir
		name = message.name
		overwrites = message.overwrites

		sandbox = sandbox if sandbox else settings.DEFAULT_SANDBOX_DIR

		exp, details = self.start_experiment_process(sandbox, launch_file, name, overwrites)

		if exp is None:
			print "failed to launch experiment process"
			send_msg(sock, self.mtool.fill_msg("rq_error", request=vars(message),
								err_code='launch_error', details=details))
		else:
			print "{0} [{1}] -- experiment process launched:  {2}".format(
										self.name, self.peer_type(), exp.pid)
			if sock.socket_type in [zmq.REP, zmq.ROUTER]:
				self.client_rq = (message, sock)


	@msg_handlers.handler("list_experiments")
	def handle_list_experiments(self, message, sock):
		exp_data = {}
		for exp_id in self.experiments:
			exp_data[exp_id] = self.experiments[exp_id].info()

		nearby = self.nearby_server_addrs()
		info = '\n{'
		for srv in nearby:
			info += '\n' + srv + ' : ' + nearby[srv][1].sender_ip + ','
		info += '}'
		print "{0} [{1}] -- nearby servers:  count: {2}, {3}".format(
										self.name, self.peer_type(), len(nearby),
										info)

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


	@msg_handlers.handler("get_experiment_contact")
	def handle_get_experiment_contact(self, message, sock):
		print "##### rq contact for: ", message.strname

		info = self._handle_match_name(message, sock)
		if info:
			send_msg(sock, self.mtool.fill_msg("experiment_contact",
												uuid=info.uuid,
												name=info.name,
												rep_addrs=info.rep_addrs,
												pub_addrs=info.pub_addrs,
												machine=info.origin_machine,
												status_name=info.status_name,
												details=info.details))


	@msg_handlers.handler("experiment_status_change")
	def handle_experiment_status_change(self, message, sock):
		exp = self.experiments.get(message.uuid, None)
		if not exp:
			if sock.socket_type in [zmq.REP, zmq.ROUTER]:
				print '##########'
				send_msg(sock, self.mtool.fill_msg('rq_error', err_code='experiment_not_found'))
			return
		exp.status_name = message.status_name
		exp.details = message.details
		if sock.socket_type in [zmq.REP, zmq.ROUTER]:
			print "%%%%%%%%"
			send_msg(sock, self.mtool.fill_msg('rq_ok'))
			
		send_msg(self._publish_socket, message.SerializeToString())

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


	@msg_handlers.handler("kill_experiment")
	def handle_kill_experiment(self, message, sock):
		match = self._handle_match_name(message, sock, this_machine=True)

		if match:
			if match.kill_timer is not None:
				send_msg(sock, self.mtool.fill_msg("rq_error", err_code="already_killed",
									details="Experiment already shutting down"))

			elif not message.force:
				print "{0} [{1}] - sending kill to experiment {2} ({3})".format(
									self.name, self.peer_type(),match.uuid, match.name)
				send_msg(self.exp_pub,
						self.mtool.fill_msg("kill", receiver=match.uuid))

				send_msg(sock, self.mtool.fill_msg("kill_sent", experiment_id=match.uuid))
				pid = match.experiment_pid
				uid = match.uuid
				print "{0} [{1}]  Waiting for experiment process {2} to terminate".format(
															self.name, self.peer_type(), uid)
				match.kill_timer = threading.Timer(1.1,
									self._handle_killing_exp, args=[pid, uid])
				match.kill_timer.start()
				send_msg(self._publish_socket, self.mtool.fill_msg('kill_sent',
					experiment_id=match.uuid
					))



	def _handle_killing_exp(self, pid, uid):
		proc = self.subprocess_mgr.process(self.machine, pid)
		if proc.process_is_running():
			proc.kill()
		print "{0} [{1}] - experiment {2} FINISHED".format(
									self.name, self.peer_type(), uid)
		proc.delete = True
		del self.experiments[uid]

		return proc.popen_obj.returncode


	@msg_handlers.handler("launch_process")
	def handle_launch_process(self, message, sock):
		if message.proc_type == 'obci_process_supervisor':
			self._handle_launch_process_supervisor(message, sock)


	def _handle_launch_process_supervisor(self, message, sock):
		sv_obj, details = self._start_obci_supervisor_process( message)

		print "LAUNCH PROCESS SV   ", sv_obj, details
		if sv_obj:
			self.exp_process_supervisors[message.sender] = sv_obj
			send_msg(sock,
					self.mtool.fill_msg("launched_process_info",
											sender=self.uuid, machine=self.machine,
											pid=sv_obj.pid, proc_type=sv_obj.proc_type,
											name=sv_obj.name,
											path=sv_obj.path))
			print "CONFIRMED LAUNCH"
		else:
			send_msg(sock, self.mtool.fill_msg('rq_error', request=message.dict(),
												err_code="launch_error",
												details=details))
			print "LAUNCH FAILURE"


	@msg_handlers.handler("kill_process_supervisor")
	def handle_kill_process_supervisor(self, message, sock):
		proc = self.exp_process_supervisors.get(message.sender, None)
		if not proc:
			send_msg(sock, self.mtool.fill_msg("rq_error", err_code="experiment_not_found"))
		else:
			#TODO
			proc.kill()

			send_msg(sock, self.mtool.fill_msg("rq_ok"))
			del self.exp_process_supervisors[message.sender]


	@msg_handlers.handler("find_eeg_experiments")
	def handle_find_eeg_experiments(self, message, sock):
		send_msg(sock, self.mtool.fill_msg("rq_ok"))
		finder_thr = threading.Thread(target=find_eeg_experiments_and_push_results,
									args=[self.ctx, self.rep_addresses,
										message,
										self.nearby_server_addrs()])
		finder_thr.daemon = True
		finder_thr.start()


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
			return None, details

		return sv_obj, False


class ExperimentInfo(object):
	def __init__(self, uuid, name, rep_addrs, pub_addrs, registration_time,
							origin_machine, pid, status_name=None, details=None,
							launch_file_path=None):
		self.uuid = uuid
		self.name = name
		self.rep_addrs = rep_addrs
		self.pub_addrs = pub_addrs
		self.registration_time = registration_time
		self.origin_machine = origin_machine
		self.experiment_pid = pid
		self.kill_timer = None
		self.status_name = status_name
		self.details = details
		self.launch_file_path = launch_file_path

	def from_dict(dic):
		try:
			exp = ExperimentInfo(dic['uuid'], dic['rep_addrs'], dic['pub_addrs'],
					dic['registration_time'], dic['origin_machine'], dic['pid'])
			exp.status_name = dic.get('status_name', None)
			exp.details = dic.get('details', None)
			exp.launch_file_path = dic.get('launch_file_path', None)
			return exp, None
		except KeyError as e:
			return None, e.args

	@property
	def machine_ip(self):
		return self.origin_machine

	@property
	def pid(self):
		return self.experiment_pid

	def info(self):
		d = dict(uuid=self.uuid,
				name=self.name,
				rep_addrs=self.rep_addrs,
				pub_addrs=self.pub_addrs,
				registration_time=self.registration_time,
				origin_machine=self.origin_machine,
				experiment_pid=self.experiment_pid,
				status_name=self.status_name,
				details=self.details,
				launch_file_path=self.launch_file_path)

		return d


def server_arg_parser(add_help=False):
	parser = argparse.ArgumentParser(parents=[basic_arg_parser()],
							description="OBCI Server : manage OBCI experiments.",
							add_help=add_help)

	parser.add_argument('--name', default='obci_server',
	                   help='Human readable name of this process')
	return parser


if __name__ == '__main__':
	parser = server_arg_parser(add_help=True)

	args = parser.parse_args()

	srv = OBCIServer(args.rep_addresses, args.pub_addresses, args.name)

	srv.run()