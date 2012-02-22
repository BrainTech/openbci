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
	return addr.startswith('tcp://'+ext_ip(ifname='lo')) or\
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

def ext_ip(peer_ip=None, ifname=None):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	client_ip = ''
	if ifname:
		try:
			client_ip = str(socket.inet_ntoa(fcntl.ioctl(
												s.fileno(),
												0x8915,  # SIOCGIFADDR
												struct.pack('256s', ifname[:15])
										)[20:24]))
		except IOError as e:
			print "ext_ip(ifname:  {0}): {1}".format(ifname, e)
			if ifname != 'lo':

				client_ip = ext_ip(peer_ip, ifname='lo')
	else:
		peer_ip = peer_ip if peer_ip else 'google.com'
		try:
			s.connect((peer_ip, 9))
			client_ip = s.getsockname()[0]
		except socket.error as e:
			print "ext_ip(peer_ip: {0}):  {1}".format(peer_ip, e)
			client_ip = lo_ip()

	del s
	return client_ip



def server_address(sock_type='rep', local=False, ifname=None, peer_ip=None):
	parser = __parser_main_config_file()

	if sock_type == 'rep':
		port = parser.get('server', 'port')
	else:
		port = parser.get('server', 'pub_port')
	if not ifname and not peer_ip:
		ifname = parser.get('server', 'ifname')

	ip = lo_ip() if local else ext_ip(ifname=ifname, peer_ip=peer_ip)
	return 'tcp://' + ip + ':' + port

def server_ifname():
	parser = __parser_main_config_file()
	return parser.get('server', 'ifname')

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
	#print ext_ip()
	print __file__
	print INSTALL_DIR