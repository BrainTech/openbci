#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

from obci.drivers.generic import py_amplifier
from multiplexer.multiplexer_constants import peers, types
from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash

import obci.drivers.balance.wii__board_xwiimote as wii_board_xwiimote
import obci.drivers.balance.wii_board_xwiimote_dummy as wii_board_dummy

class PyAmplifierWiiBoard(py_amplifier.PyAmplifier):
    @log_crash
    def __init__(self, addresses):
        super(PyAmplifierWiiBoard, self).__init__(addresses=addresses, peer_type=peers.WII_BOARD_AMPLIFIER)

        if self.get_param("amplifier_online") == 'True':
            self.logger.info("Start initialize Wii Board amplifier...")
            try:
                self.wbb = wii_board_xwiimote.WiiBalanceBoard()
            except Exception as error:
                self.logger.error("{} ABORDING...".format(error))
                sys.exit(1)
            finally:
                self.logger.info("Connect to Wii Board!")

        elif self.get_param("amplifier_online") == 'False':
            self.logger.info("Start initialize Wii Board dummy amplifier...")
            self.wbb = wii_board_dummy.WiiBalanceBoard()
            self.logger.info("Connect to Wii Board!")

        else:
            self.logger.error("Parametr amplifier_online is wrong (posibble: True/False) ABORDING...")
            sys.exit(1)

    def _manage_params(self):
        super(PyAmplifierWiiBalanceBoard, self)._manage_params() 
        self.mx_signal_type = types.WII_BOARD_SIGNAL_MESSAGE
        active_channels = self.get_param('active_channels').split(';')
        channel_names = self.get_param('channel_names').split(';')
        if len(channel_names) == len(active_channels):
            self.set_param('channel_gains', ';'.join([str(1.0) for i in channel_names]))
            self.set_param('channel_offsets', ';'.join([str(0.0) for i in channel_names]))
        else:
            self.logger.error("Number of active channels is not equal to number of channels names!! ABORDING...")
            sys.exit(1)
        self.samples_per_packet = int(self.get_param('samples_per_packet'))
        self.sampling_rate = int(self.get_param('sampling_rate'))

    def _get_msg(self):
        samples = []
        for i in range(self.samples_per_packet):
            s, ts = self._get_sample()
            #print s,ts
            samples.append((s, ts))
        return self._create_msg(samples)

    @log_crash            
    def do_sampling(self):
        while True:
            msg = self._get_msg()
            mx_msg = self._create_mx_msg(msg)
            self._send(mx_msg)

    def _get_sample(self):
        return self.wbb.measurement()


if __name__ == "__main__":
    PyAmplifierWiiBoard(settings.MULTIPLEXER_ADDRESSES).do_sampling()