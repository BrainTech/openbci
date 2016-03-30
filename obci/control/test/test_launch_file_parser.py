#!/usr/bin/python
# -*- coding: utf-8 -*-
import io

from obci.control.launcher import system_config, launch_file_parser

class TestLaunchFileParser(object):

    def setup(self):
        self.txt = """
[peers]

; costam costam

[peers.p_a]

path=control/test/peer_a.py
config=control/test/peer_a.ini

[peers.p_a.config_sources]

peerb=p_b

;***********************************************

[peers.p_b]

path=control/test/peer_b.py
config=control/test/peer_b.ini

[peers.p_b.config_sources]
peer1=p_a
"""
        self.cf = system_config.OBCISystemConfig()
        self.pr = launch_file_parser.LaunchFileParser("/host/dev/openbci", "~/.obci/scenarios")

    def test_sth(self):
        self.pr.parse(io.BytesIO(self.txt), self.cf)
        assert 0
