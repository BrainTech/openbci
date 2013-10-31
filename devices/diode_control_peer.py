#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#      Krzysztof Kulewski <kulewski@gmail.com>
#      Magdalena Michalska <jezzy.nietoperz@gmail.com>
#      Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>
#

import time 

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash

class DiodeControl(ConfiguredMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    @log_crash
    def __init__(self, addresses):
        super(DiodeControl, self).__init__(addresses=addresses,
                                          type=peers.SUPER_DIODE)
        self.blinker = None
        self._init_blinker()

        self._init_freqs()

        start = int(self.config.get_param("blink_on_start"))
        if start:
            self.start_blinking()

        self.ready()

    def _init_blinker(self):
        raise Exception("To be subclassed!")

    def _init_freqs(self):
        freqs_str = self.config.get_param("freqs")
        freqs = freqs_str.split(";")
        self.on_freqs_str = ';'.join([str(i) for i in [-1]*len(freqs)])
        self.off_freqs_str = ';'.join([str(i) for i in [0]*len(freqs)])
        self.update_freqs(freqs_str)

    def update_freqs(self, freqs_str):
        self.freqs_str = freqs_str
        try:
            self.freqs = [int(i) for i in freqs_str.split(";")]
        except ValueError: #'' in freqs - means turn diodes on
            self.logger.warning("Got nonumeric freqs. Set to -1")
            self.freqs = [-1 for i in freqs_str.split(";")]

    def start_blinking(self):
        self.blinker.blinkSSVEP(self.freqs, 1, 1)
        self._send_diode_message(self.freqs_str)
    
    def diodes_on(self):
        self.blinker.on()
        self._send_diode_message(self.on_freqs_str)
    
    def diodes_off(self):
        self.blinker.off()
        self._send_diode_message(self.off_freqs_str)
    
    def handle_message(self, mxmsg):
        """Handle DIODE_CONTROL_MESSAGE of Variable type.
        expected commands are:
        - .key == 'start' - start blinking with current freqs
        - .key == 'stop' - stop blinking
        - .key == 'update' - update blinker with values in value
          eg. we might get .value == "1;2;3;4;5;6;7;8" meaning
          that we are to blink those values.
          Additionaly if .value[0] == -1 we turn in 'static ligth' mode."""

        if mxmsg.type == types.DIODE_CONTROL_MESSAGE:
	    l_msg = variables_pb2.Variable()
            l_msg.ParseFromString(mxmsg.message)
            if l_msg.key == 'stop':
                self.logger.info("Stop blinker!")
                self.diodes_on()
            elif l_msg.key == 'start':
                self.logger.info("Start blinker!")
                self.start_blinking()
            elif l_msg.key == 'update':
                self.logger.info('Update blinker!')
                self.logger.info(l_msg.value)
                self.update_freqs(l_msg.value)
                self.start_blinking()
            else:
                self.logger.warning("Unrecognised blink control message! "+str(l_msg.key))
        self.no_response()

    def _send_diode_message(self, freqs_str):
        msg = variables_pb2.Diode()
        msg.value = freqs_str
        msg.timestamp = time.time()
        self.conn.send_message(message = msg.SerializeToString(), 
        type = types.DIODE_MESSAGE, flush=True)
