#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#      Krzysztof Kulewski <kulewski@gmail.com>
#      Magdalena Michalska <jezzy.nietoperz@gmail.com>
#      Mateusz Kruszyński <mateusz.kruszynski@titanis.pl>
#

from multiplexer.multiplexer_constants import peers, types
from peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from configs import settings, variables_pb2

from devices import devices_logging as logger
LOGGER = logger.get_logger('diode_control_peer')

class DiodeControl(ConfiguredMultiplexerServer):
    """A class for creating a manifest file with metadata."""
    def __init__(self, addresses):
        super(InfoSaver, self).__init__(addresses=addresses,
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
        self.on_freqs_str = ';'.join([-1]*len(freqs))
        self.off_freqs_str = ';'.join([0]*len(freqs))
        self.update_freqs(freqs_str)

    def update_freqs(self, freqs_str):
        self.freqs_str = freqs_str
        self.freqs = [int(i) for i in freqs_str.split(";")]

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
                LOGGER.info("Stop blinker!")
                self.diodes_on()
            elif l_msg.key == 'start':
                LOGGER.info("Start blinker!")
                self.start_blinking()
            elif l_msg.key == 'update':
                self.update_freqs(l_msg.value)
                if self.freqs[0] == -1:
                    self.diodes_on()
                else:
                    self.start_blinking()
            else:
                LOGGER.warning("Unrecognised blink control message! "+str(l_msg.key))
        self.no_response()

    def _send_diode_message(self, freqs_str):
        msg = variables_pb2.Variable()
        msg.key = 'update'
        msg.vlue = freqs_str
        self.conn.send_message(message = msg.SerializeToString(), 
        type = types.DIODE_MESSAGE, flush=True)
