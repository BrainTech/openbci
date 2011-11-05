#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading

import zmq

from obci_machine import OBCIMachine
from obci_controller_messages import fill_msg, decode_msg

class OBCIController(object):

	def __init__(self, obci_install_dir, address, port, other_addresses,
													name='controller'):
		self.address = address
		self.port = port
		self.other_addrs = other_addresses
		self.name = name
		self.obci_install_dir = obci_install_dir
		self.agents = {}
		self.machines = {}
		self.main_machine = None

		self.machine_thread = None
		self.ctx = zmq.Context()

	def net_init(self):

		self.server = self.ctx.socket(zmq.REP)
		addr = self.address + ':' + self.port
		print addr
		self.server.bind(addr)

		# PUB & SUB & REQ

	def start_obci_machine(self):
		machine = OBCIMachine(self.address, self.obci_install_dir,
								self.address+':'+self.port, self.name)
		machine.net_init()


	def run(self):
		self.machine_thread = threading.Thread(None, self.start_obci_machine)
		self.machine_thread.start()

		msg = self.server.recv()
		print msg
		self.server.send(fill_msg("ok"))

if __name__ == '__main__':
	cntrl = OBCIController('/host/dev/openbci', 'tcp://127.0.0.1', '22222', None, 'tralala')
	cntrl.net_init()
	cntrl.run()