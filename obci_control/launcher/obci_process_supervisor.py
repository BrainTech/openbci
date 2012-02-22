#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import uuid
import subprocess
import argparse

import zmq
import socket

from common.message import OBCIMessageTool, send_msg, recv_msg
from launcher_messages import message_templates
import common.net_tools as net
import common.obci_control_settings as settings


from obci_control_peer import OBCIControlPeer, basic_arg_parser
import launcher_tools

import subprocess_monitor
from subprocess_monitor import SubprocessMonitor, TimeoutDescription,\
STDIN, STDOUT, STDERR, NO_STDIO, RETURNCODE, DEFAULT_TAIL_RQ

class OBCIProcessSupervisor(OBCIControlPeer):

	msg_handlers = OBCIControlPeer.msg_handlers.copy()

	def __init__(self, sandbox_dir,
										source_addresses=None,
										source_pub_addresses=None,
										rep_addresses=None,
										pub_addresses=None,
										name='obci_process_supervisor'):

		self.peers = {}
		self.status = launcher_tools.ExperimentStatus()
		self.source_pub_addresses = source_pub_addresses
		self.ip = net.ext_ip(ifname=net.server_ifname())
		self.sandbox_dir = sandbox_dir if sandbox_dir else settings.DEFAULT_SANDBOX_DIR
		self.ctx = zmq.Context()
		self.mx_data = self.set_mx_data()
		self.env = self.peer_env(self.mx_data)
		self.launch_data = []
		self.processes = {}

		super(OBCIProcessSupervisor, self).__init__(
											source_addresses=source_addresses,
											rep_addresses=rep_addresses,
											pub_addresses=pub_addresses,
											name=name)
		self.subprocess_mgr = SubprocessMonitor(self.ctx, self.uuid)

	def _handle_registration_response(self, response):
		self.launch_data = response.params
		print self.name,'[', self.type, ']',  "RECEIVED LAUNCH DATA: ", self.launch_data


	def set_mx_data(self):

		src_ = net.choose_not_local(self.source_pub_addresses)[:1]
		if not src_:
			src_ = net.choose_local(self.source_pub_addresses, ip=True)[:1]
		src = src_[0]
		src = src[6:].split(':')[0]

		if src == socket.gethostname():
			sock = self.ctx.socket(zmq.REP)
			port = str(sock.bind_to_random_port("tcp://" + self.ip,
											min_port=settings.PORT_RANGE[0],
											max_port=settings.PORT_RANGE[1]))
			sock.close()
			return (self.ip, port), "" #empty passwd
		else:
			return None, None

	def mx_addr_str(self, mx_data):
		if mx_data[0] is None:
			return None
		addr, port = mx_data[0]
		print self.name,'[', self.type, ']', "mx addr str", addr + ':' + str(port)
		return addr + ':' + str(port)


	def peer_env(self, mx_data):

		if mx_data[0] is None:
			return None

		env = os.environ.copy()
		addr, port = mx_data[0]

		_env = {
			"MULTIPLEXER_ADDRESSES": str(addr) + ':' + str(port),
			"MULTIPLEXER_PASSWORD": mx_data[1],
			"MULTIPLEXER_RULES": launcher_tools.mx_rules_path()
		}
		env.update(_env)
		return env

	def peer_type(self):
		return "obci_process_supervisor"

	def net_init(self):
		self.source_sub_socket = self.ctx.socket(zmq.SUB)
		self.source_sub_socket.setsockopt(zmq.SUBSCRIBE, "")

		self._all_sockets.append(self.source_sub_socket)

		if self.source_pub_addresses:
			for addr in self.source_pub_addresses:
				self.source_sub_socket.connect(addr)

		(self.config_server_socket, self.cs_addresses) = self._init_socket([], zmq.SUB)
		self.cs_addr = net.choose_not_local(self.cs_addresses)
		if not self.cs_addr:
			self.cs_addr = net.choose_local(self.cs_addresses)[0]
		else:
			self.cs_addr = self.cs_addr[0]
		self.config_server_socket.setsockopt(zmq.SUBSCRIBE, "")
		self._all_sockets.append(self.config_server_socket)
		
		super(OBCIProcessSupervisor, self).net_init()

	def params_for_registration(self):
		return dict(pid=os.getpid(), machine=self.ip,
					mx_data=[self.mx_addr_str(self.mx_data), self.mx_data[1]])

	def custom_sockets(self):
		return [self.source_sub_socket, self.config_server_socket]

	@msg_handlers.handler("start_mx")
	def handle_start_mx(self, message, sock):
		if 'mx' in self.launch_data and self.mx_data[0] is not None:
			print self.name,'[', self.type, ']', "..starting multiplexer"
			path = launcher_tools.mx_path()
			if message.args:
				args = message.args
			else:
				args = ['run_multiplexer', self.mx_addr_str(self.mx_data),
						'--multiplexer-password', self.mxdata[1],
						'--rules', launcher_tools.mx_rules_path()]
			proc, details = self._launch_process(path, args, 'multiplexer', 'mx',
												env=self.env)
			self.processes['mx'] = proc
			if proc is not None:
				self.mx = proc


	@msg_handlers.handler("start_peers")
	def handle_start_peers(self, message, sock):
		proc, details = None, None
		success = True
		path, args = None, None

		ldata = []
		ldata.append(('config_server', self.launch_data['config_server']))
		if 'amplifier' in self.launch_data:
			ldata.append(('amplifier', self.launch_data['amplifier']))
		for peer, data in self.launch_data.iteritems():
			if (peer, data) not in ldata:
				ldata.append((peer, data))

		for peer, data in ldata:#self.launch_data.iteritems():
			if peer.startswith('mx'):
				continue
			path = os.path.join(launcher_tools.obci_root(), data['path'])
			args = data['args']
			if peer.startswith('config_server'):
				args += ['-p', 'launcher_socket_addr', self.cs_addr]
			proc, details = self._launch_process(path, args, data['peer_type'],
														peer, env=self.env, capture_io=NO_STDIO)
			if proc is not None:
				self.processes[peer] = proc
			else:
				success = False
				break
		if success:
			send_msg(self._publish_socket, self.mtool.fill_msg("all_peers_launched",
													machine=self.ip))
		else:
			print self.name,'[', self.type, ']', "OBCI LAUNCH FAILED"
			send_msg(self._publish_socket, self.mtool.fill_msg("obci_launch_failed",
													machine=self.ip, path=path,
													args=args, details=details))
			self.processes = {}
			self.subprocess_mgr.killall()


	def _launch_process(self, path, args, proc_type, name,
									env=None, capture_io=NO_STDIO):
		proc, details = self.subprocess_mgr.new_local_process(path, args,
														proc_type=proc_type,
														name=name,
														monitoring_optflags=RETURNCODE,
														capture_io=capture_io,
														env=env)
		if proc is None:
			print self.name,'[', self.type, ']', "process launch FAILED:", path, args
			send_msg(self._publish_socket, self.mtool.fill_msg("launch_error",
											sender=self.uuid,
											details=dict(machine=self.ip, path=path, args=args,
														error=details)))
		else:
			print self.name,'[', self.type, ']', "process launch success:", path, args
			send_msg(self._publish_socket, self.mtool.fill_msg("launched_process_info",
											sender=self.uuid,
											machine=self.ip,
											pid=proc.pid,
											proc_type=proc_type, name=name,
											path=path,
											args=args))
		return proc, details

	@msg_handlers.handler("get_tail")
	def handle_get_tail(self, message, sock):
		lines = message.len if message.len else DEFAULT_TAIL_RQ
		peer = message.peer_id
		if peer not in self.launch_data:
			return
		experiment_id = self.launch_data[peer]['experiment_id']
		txt = self.processes[peer].tail_stdout(lines=lines)
		send_msg(self._publish_socket, self.mtool.fill_msg("tail", txt=txt,
													sender=self.uuid,
													experiment_id=experiment_id,
												peer_id=peer))

	@msg_handlers.handler("stop_all")
	def handle_stop_all(self, message, sock):

		self.subprocess_mgr.killall()

	@msg_handlers.handler("dead_process")
	def handle_dead_process(self, message, sock):
		proc = self.subprocess_mgr.process(message.machine, message.pid)
		if proc is not None:
			proc.mark_delete()
			if proc.proc_type == 'obci_peer' or proc.proc_type == 'multiplexer':
				send_msg(self._publish_socket, self.mtool.fill_msg("obci_peer_dead",
												sender=self.uuid,
												sender_ip=self.ip,
												peer_id=proc.name,
												path=proc.path,
												status=proc.status()
												))

	@msg_handlers.handler("obci_peer_registered")
	def handle_obci_peer_registered(self, message, sock):
		send_msg(self._publish_socket, message.SerializeToString())

	@msg_handlers.handler("obci_peer_params_changed")
	def handle_obci_peer_params_changed(self, message, sock):
		send_msg(self._publish_socket, message.SerializeToString())

	@msg_handlers.handler("obci_peer_ready")
	def handle_obci_peer_ready(self, message, sock):
		send_msg(self._publish_socket, message.SerializeToString())

	def cleanup_before_net_shutdown(self, kill_message, sock=None):
		self.processes = {}
		#self.subprocess_mgr.killall()

	def clean_up(self):
		print self.name,'[', self.type, ']',  "cleaning up"
		self.processes = {}
		self.subprocess_mgr.killall()
		self.subprocess_mgr.delete_all()


def process_supervisor_arg_parser():
	parser = argparse.ArgumentParser(parents=[basic_arg_parser()],
					description='A process supervisor for OBCI Peers')
	parser.add_argument('--sv-pub-addresses', nargs='+',
					help='Addresses of the PUB socket of the supervisor')
	parser.add_argument('--sandbox-dir',
					help='Directory to store temporary and log files')

	parser.add_argument('--name', default='obci_process_supervisor',
					help='Human readable name of this process')
	return parser


if __name__ == '__main__':
	parser = process_supervisor_arg_parser()
	args = parser.parse_args()

	process_sv = OBCIProcessSupervisor(args.sandbox_dir,
							source_addresses=args.sv_addresses,
							source_pub_addresses=args.sv_pub_addresses,
							rep_addresses=args.rep_addresses,
							pub_addresses=args.pub_addresses,
							name=args.name)
	process_sv.run()