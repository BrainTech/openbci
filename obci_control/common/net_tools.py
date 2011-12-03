#!/usr/bin/python
# -*- coding: utf-8 -*-

import zmq
import socket
import os
import ConfigParser

from common.obci_control_settings import PORT_RANGE, INSTALL_DIR, OBCI_HOME_DIR, MAIN_CONFIG_NAME


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

def choose_local(addrs):
	result = [a for a in addrs if a.startswith('ipc://')]
	if not result:
		result += [a for a in addrs if a == 'tcp://'+lo_ip()]
	return result

def choose_not_local(addrs):
	result = [a for a in addrs if a.startswith('tcp://') and not a == 'tcp://'+lo_ip()]
	if not result:
		result += [a for a in addrs if a.startswith('tcp://')]
	return result

def lo_ip():
	return '127.0.0.1'

def ext_ip():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
	    s.connect(('google.com', 9))
	    client_ip = s.getsockname()[0]
	except socket.error:
	    client_ip = lo_ip()
	finally:
	    del s
	return client_ip


def server_address(sock_type='rep', local=False):
	parser = __parser_main_config_file()

	if sock_type == 'rep':
		port = parser.get('server', 'port')
	else:
		port = parser.get('server', 'pub_port')

	ip = lo_ip() if local else ext_ip()
	return 'tcp://' + ip + ':' + port

def __parser_main_config_file():
	directory = os.path.abspath(OBCI_HOME_DIR)

	filename = MAIN_CONFIG_NAME
	fpath = os.path.join(directory, filename)

	parser = None
	if os.path.exists(fpath):
		parser = ConfigParser.RawConfigParser()
		with open(fpath) as f:
			parser.readfp(f)
	else:
		print "Main config file not found in {0}".format(directory)
		raise OBCISystemError()
	return parser

def server_pub_port():
	parser = __parser_main_config_file()
	port = parser.get('server', 'pub_port')
	return port

def server_rep_port():
	parser = __parser_main_config_file()
	port = parser.get('server', 'port')
	return port

if __name__ == '__main__':
	print ext_ip()
	print __file__
	print INSTALL_DIR