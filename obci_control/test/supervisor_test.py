#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import uuid
import subprocess
import argparse
import time

import zmq
import socket

from common.message import OBCIMessageTool, send_msg, recv_msg
from launcher.launcher_messages import message_templates
import common.net_tools as net
import common.obci_control_settings as settings


from launcher.obci_control_peer import OBCIControlPeer, basic_arg_parser
import launcher.launcher_tools as launcher_tools

import launcher.subprocess_monitor as subprocess_monitor
from launcher.subprocess_monitor import SubprocessMonitor, TimeoutDescription,\
STDIN, STDOUT, STDERR, NO_STDIO, RETURNCODE, DEFAULT_TAIL_RQ

class OBCIProcessSupervisor(OBCIControlPeer):

	msg_handlers = OBCIControlPeer.msg_handlers.copy()

	def __init__(self, sandbox_dir,
										source_addresses=None,
										source_pub_addresses=None,
										rep_addresses=None,
										pub_addresses=None,
										experiment_uuid='',
										name='obci_process_supervisor'):

		self.peers = {}
		self.status = launcher_tools.READY_TO_LAUNCH
		self.source_pub_addresses = source_pub_addresses
		self.machine = socket.gethostname()
		self.sandbox_dir = sandbox_dir if sandbox_dir else settings.DEFAULT_SANDBOX_DIR
		self.ctx = zmq.Context()
		self.mx_data = self.set_mx_data()
		self.env = self.peer_env(self.mx_data)
		self.launch_data = []
		self.peer_order = []
		self._running_peer_order = []
		self._current_part = None
		self.experiment_uuid = experiment_uuid
		self.peers_to_launch = []
		self.processes = {}
		self.restarting = []

		super(OBCIProcessSupervisor, self).__init__(
											source_addresses=source_addresses,
											rep_addresses=rep_addresses,
											pub_addresses=pub_addresses,
											name=name)
		self.subprocess_mgr = SubprocessMonitor(self.ctx, self.uuid)


	def peer_type(self):
		return "obci_process_supervisor"

	def net_init(self):
		self.source_sub_socket = self.ctx.socket(zmq.SUB)
		self.source_sub_socket.setsockopt(zmq.SUBSCRIBE, "")

		self._all_sockets.append(self.source_sub_socket)

		if self.source_pub_addresses:
			for addr in self.source_pub_addresses:
				self.source_sub_socket.connect(addr)

		(self.config_server_socket, self.cs_addresses) = self._init_socket([], zmq.PULL)
		# self.config_server_socket.setsockopt(zmq.SUBSCRIBE, "")

		self.cs_addr = net.choose_not_local(self.cs_addresses)
		if not self.cs_addr:
			self.cs_addr = net.choose_local(self.cs_addresses)[0]
		else:
			self.cs_addr = self.cs_addr[0]

		self._all_sockets.append(self.config_server_socket)

		super(OBCIProcessSupervisor, self).net_init()

	def params_for_registration(self):
		return dict(pid=os.getpid(), machine=self.machine,
					mx_data=[self.mx_addr_str(((socket.gethostname(), self.mx_data[0][1]), self.mx_data[1])), self.mx_data[1]])

	def custom_sockets(self):
		return [self.source_sub_socket, self.config_server_socket]


	def _handle_registration_response(self, response):
		self.launch_data = response.params['launch_data']
		self.peers_to_launch = list(self.launch_data.keys())
		self.peer_order = response.params['peer_order']
		for part in self.peer_order:
			self._running_peer_order.append(list(part))
		print self.name,'[', self.type, ']',  "RECEIVED LAUNCH DATA: ", self.launch_data


	def set_mx_data(self):

		src_ = net.choose_not_local(self.source_pub_addresses)[:1]
		if not src_:
			src_ = net.choose_local(self.source_pub_addresses, ip=True)[:1]
		src = src_[0]
		src = src[6:].split(':')[0]

		if src == socket.gethostname():
			sock = self.ctx.socket(zmq.REP)
			port = str(sock.bind_to_random_port("tcp://127.0.0.1", 
											min_port=settings.PORT_RANGE[0],
											max_port=settings.PORT_RANGE[1]))
			sock.close()
			return ('0.0.0.0', port), "" #empty passwd
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
			"MULTIPLEXER_ADDRESSES": socket.gethostname() + ':' + str(port),
			"MULTIPLEXER_PASSWORD": mx_data[1],
			"MULTIPLEXER_RULES": launcher_tools.mx_rules_path()
		}
		env.update(_env)
		return env

	@msg_handlers.handler("start_mx")
	def handle_start_mx(self, message, sock):
		if 'mx' in self.launch_data and self.mx_data[0] is not None:
			print self.name,'[', self.type, ']', "..starting multiplexer"
			self.peer_order.remove(['mx'])
			self.peers_to_launch.remove('mx')
			path = launcher_tools.mx_path()

			args = ['run_multiplexer', self.mx_addr_str(
								(('0.0.0.0', self.mx_data[0][1]), self.mx_data[1])),
					'--multiplexer-password', self.mx_data[1],
					'--rules', launcher_tools.mx_rules_path()]
			proc, details = self._launch_process(path, args, 'multiplexer', 'mx',
												env=self.env)
			self.processes['mx'] = proc
			if proc is not None:
				self.mx = proc


	@msg_handlers.handler("start_peers")
	def handle_start_peers(self, message, sock):
		self._launch_processes(self.launch_data)

	def test(self):
		# for i in range(SEND):
		#     send_msg(self.push, str(i))
		self.pull = self.ctx.socket(zmq.SUB)
		self.pull.bind('tcp://*:16789')

		received = 0
		prev = -1
		for i in range(SEND):
			msg = recv_msg(self.pull)
			if int(msg):
				# prev = int(msg)
				received += 1
			if received % 10000 == 0:
				print "zmq: received ", received, "messages, last: ", msg

		if received == SEND:
			print "zmq: OK"
		else:
			print "WUT?", received
		# self.push.close()
		self.pull.close()


	@msg_handlers.handler("manage_peers")
	def handle_manage_peers(self, message, sock):
		if not message.receiver == self.uuid:
			return
		message.kill_peers.append('config_server')
		
		message.start_peers_data['config_server'] = dict(self.launch_data['config_server'])
		restore_config = [peer for peer in self.processes if peer not in message.kill_peers]
		for peer in message.kill_peers:
			proc = self.processes.get(peer, None)
			if not proc:
				print self.name,'[', self.type, ']', "peer to kill not found:", peer
				continue
			print "MORPH:  KILLING ", peer
			proc.kill()
			print "MORPH:  KILLED ", peer
			del self.processes[peer]
			del self.launch_data[peer]

		for peer, data in message.start_peers_data.iteritems():
			self.launch_data[peer] = data
		self.restarting = [peer for peer in message.start_peers_data if peer in message.kill_peers]
		
		self._launch_processes(message.start_peers_data, restore_config=restore_config)


	def _launch_processes(self, launch_data, restore_config=[]):
		proc, details = None, None
		success = True
		path, args = None, None

		self.status = launcher_tools.LAUNCHING

		ldata = []
		if 'config_server' in launch_data:
			ldata.append(('config_server', launch_data['config_server']))
		if 'amplifier' in launch_data:
			ldata.append(('amplifier', launch_data['amplifier']))
		for peer, data in launch_data.iteritems():
			if (peer, data) not in ldata:
				ldata.append((peer, data))

		for peer, data in ldata:#self.launch_data.iteritems():
			wait = 0
			if peer.startswith('mx'):
				continue
			path = os.path.join(launcher_tools.obci_root(), data['path'])
			args = data['args']
			if peer.startswith('config_server'):
				args += ['-p', 'launcher_socket_addr', self.cs_addr]
				args += ['-p', 'experiment_uuid', self.experiment_uuid]
				
				if restore_config:
					args += ['-p', 'restore_peers', ' '.join(restore_config)]
				wait = 0.4
			proc, details = self._launch_process(path, args, data['peer_type'],
														peer, env=self.env, capture_io=NO_STDIO)
			if proc is not None:
				self.processes[peer] = proc
			else:
				success = False
				break
			time.sleep(wait)
		if success:
			send_msg(self._publish_socket, self.mtool.fill_msg("all_peers_launched",
													machine=self.machine))
		else:
			print self.name,'[', self.type, ']', "OBCI LAUNCH FAILED"
			send_msg(self._publish_socket, self.mtool.fill_msg("obci_launch_failed",
													machine=self.machine, path=path,
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
											details=dict(machine=self.machine, path=path, args=args,
														error=details)))
		else:
			print self.name,'[', self.type, ']', "process launch success:", path, args, proc.pid
			send_msg(self._publish_socket, self.mtool.fill_msg("launched_process_info",
											sender=self.uuid,
											machine=self.machine,
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


	@msg_handlers.handler("experiment_finished")
	def handle_experiment_finished(self, message, sock):
		pass

	@msg_handlers.handler("morph_to_new_scenario")
	def handle_morph(self, message, sock):
		pass

	@msg_handlers.handler("stop_all")
	def handle_stop_all(self, message, sock):

		self.subprocess_mgr.killall()

	@msg_handlers.handler("dead_process")
	def handle_dead_process(self, message, sock):
		proc = self.subprocess_mgr.process(message.machine, message.pid)
		if proc is not None:
			proc.mark_delete()
			name = proc.name
			print '~~~~~   ~~~~~   ', name, self.restarting, message.status[0]

			if (proc.proc_type == 'obci_peer' or proc.proc_type == 'multiplexer') and \
								not (name in self.restarting and message.status[0] == 'terminated'):
				print "KILLLLLING     and sending obci_peer_dead", proc.name
				send_msg(self._publish_socket, self.mtool.fill_msg("obci_peer_dead",
												sender=self.uuid,
												sender_ip=self.machine,
												peer_id=proc.name,
												path=proc.path,
												status=proc.status()
												))
			if name in self.restarting:
				self.restarting.remove(name)

	@msg_handlers.handler("obci_peer_registered")
	def handle_obci_peer_registered(self, message, sock):
		send_msg(self._publish_socket, message.SerializeToString())

	@msg_handlers.handler("obci_peer_params_changed")
	def handle_obci_peer_params_changed(self, message, sock):
		send_msg(self._publish_socket, message.SerializeToString())

	@msg_handlers.handler("obci_peer_ready")
	def handle_obci_peer_ready(self, message, sock):
		print self.name , "got!", message.type
		send_msg(self._publish_socket, message.SerializeToString())


	@msg_handlers.handler("obci_control_message")
	def handle_obci_control_message(self, message, sock):
		# ignore :)
		pass

	@msg_handlers.handler("obci_peer_dead")
	def handle_obci_control_message(self, message, sock):
		# ignore :)
		pass

	@msg_handlers.handler("process_supervisor_registered")
	def handle_supervisor_registered(self, messsage, sock):
		# also ignore
		pass

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
	parser.add_argument('--experiment-uuid', help='UUID of the parent obci_experiment')
	return parser


if __name__ == '__main__':
	# parser = process_supervisor_arg_parser()
	# args = parser.parse_args()

	process_sv = OBCIProcessSupervisor('/tmp',
							source_addresses=None,
							source_pub_addresses=None,
							rep_addresses=None,
							pub_addresses=None,
							experiment_uuid=None,
							name='test')
	process_sv.test()