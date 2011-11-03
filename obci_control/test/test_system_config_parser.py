#!/usr/bin/python
# -*- coding: utf-8 -*-
import io

from launcher import system_config, system_config_parser

class TestSystemConfigParser(object):

	def setup(self):
		self.txt = """
[peers]

; costam costam

[peers.p_a]

path=obci_control/test/peer_a.py
config=obci_control/test/peer_a.ini

[peers.p_a.config_sources]

peerb=p_b

;***********************************************

[peers.p_b]

path=openbci/obci_control/test/peer_b.py
config=path/to/another/config

[peers.p_b.config_sources]
peer1=p_a
"""
		self.cf = system_config.OBCISystemConfig()
		self.pr = system_config_parser.SystemConfigParser("/host/dev/openbci")

	def test_sth(self):
		self.pr.parse(io.BytesIO(self.txt), self.cf)
		assert 0