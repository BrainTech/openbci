#!/usr/bin/python
# -*- coding: utf-8 -*-

import zmq
import socket
import struct
import fcntl
import os
import ConfigParser

from common.obci_control_settings import PORT_RANGE, INSTALL_DIR, OBCI_HOME_DIR, MAIN_CONFIG_NAME
from common.config_helpers import OBCISystemError



def is_net_addr(addr):
	return not addr.startswith('ipc') \
			and not addr.startswith('inproc')

def addr_is_local(addr):
	return addr.startswith('tcp://localhost') or\
					addr.startswith('tcp://0.0.0.0') or\
					addr.startswith('tcp://127.0.0.1')

def choose_local(addrs, ip=False):
	result = []
	if not ip:
		result = [a for a in addrs if a.startswith('ipc://')]
	if not result:
		result += [a for a in addrs if addr_is_local(a)]
	return result

def choose_not_local(addrs):
	result = [a for a in addrs if a.startswith('tcp://') and not a.startswith('tcp://'+lo_ip())]
	#if not result:
	#	result += [a for a in addrs if a.startswith('tcp://')]
	return result

def lo_ip():
	return '127.0.0.1'

def ext_ip(peer_ip=None):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	client_ip = ''

	peer_ip = peer_ip if peer_ip else 'google.com'
	try:
		s.connect((peer_ip, 9))
		client_ip = s.getsockname()[0]
	except socket.error as e:
		print "ext_ip(peer_ip: {0}):  {1}".format(peer_ip, e)
		client_ip = lo_ip()

	del s
	return client_ip



def server_address(sock_type='rep', local=False, peer_ip=None):
	parser = __parser_main_config_file()

	if sock_type == 'rep':
		port = parser.get('server', 'port')
	else:
		port = parser.get('server', 'pub_port')


	ip = lo_ip() if local else ext_ip(peer_ip=peer_ip)
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

def server_bcast_port():
	parser = __parser_main_config_file()
	try:
		port = parser.get('server', 'bcast_port')
	except Exception, e:
		print "[ WARNING! WARNING! ] Config file is not up to date. Taking default bcast_port value!"
		port = '23123'
	return port

if __name__ == '__main__':
	#print ext_ip()
	print __file__
	print INSTALL_DIR