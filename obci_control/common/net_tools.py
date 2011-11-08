#!/usr/bin/python
# -*- coding: utf-8 -*-

import zmq
import socket

from common.obci_control_settings import PORT_RANGE, INSTALL_DIR


def public_socket(address_list, zmq_type, zmq_context, random_port=True,
															ipc_core_name=''):
	def prepare_addr(addr):
		if not random_port:
			return addr
		if len(addr.split(':')) < 3:
			return addr
		else: return addr.rsplit(':', 1)[0]

	addrs = [prepare_addr(addr) for addr in address_list]

	return __public_sock_init(zmq_type, addrs,
							zmq_context, random_port, ipc_core_name)

def __public_sock_init(zmq_type, addrs, zmq_context, random_port, ipc_core_name):

	sock = zmq_context.socket(zmq_type)
	port = None

	addresses = []
	net_addresses = [addr for addr in addrs if is_net_addr(addr)]
	other_addresses = [addr for addr in addrs if not is_net_addr(addr)]

	if random_port and net_addresses:
		addr = net_addresses.pop(0)
		port = str(sock.bind_to_random_port(addr,
											min_port=PORT_RANGE[0],
											max_port=PORT_RANGE[1]))
		addresses.append(addr + ':' + port)

	addrs_to_bind = net_addresses + other_addresses

	for addr in addrs_to_bind:
		if random_port and is_net_addr(addr):
			addr = addr + ':' + port
		sock.bind(addr)
		addresses.append(addr)

	if ipc_core_name:
		type_name = 'rep' if zmq_type == zmq.REP else 'pub'
		ipc_addr = 'ipc://' + str(type_name) + '_' + ipc_core_name + '.ipc'
		sock.bind(ipc_addr)
		addresses.append(ipc_addr)

	return (sock, addresses)

def is_net_addr(addr):
	return not addr.startswith('ipc') \
			and not addr.startswith('inproc')


def lo_ip():
	return '127.0.0.1'

def ext_ip():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
	    s.connect(('google.com', 9))
	    client_ip = s.getsockname()[0]
	except socket.error:
	    client_ip = ""
	finally:
	    del s
	return client_ip

if __name__ == '__main__':
	print ext_ip()
	print __file__
	print INSTALL_DIR