#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from multiplexer.multiplexer_constants import peers, types
from drivers.eeg.binary_driver_wrapper import BinaryDriverWrapper
from drivers import drivers_logging as logger
from obci_configs import settings
from launcher.launcher_tools import obci_root

LOGGER = logger.get_logger("AmplifierVirtual", "info")

class AmplifierGtec(BinaryDriverWrapper):
    def __init__(self, addresses):
        super(AmplifierGtec, self).__init__(addresses=addresses, type=peers.AMPLIFIER_SERVER)

    def get_run_args(self, multiplexer_address):

        host,port = multiplexer_address
        exe = self.config.get_param('driver_executable')
        exe = os.path.join(obci_root(), exe)
        v = self.config.get_param('samples_per_packet')
        simple_driver = os.path.join(os.path.dirname(exe), "simple_gtec_driver")
        rate = int(float(self.config.get_param('sampling_rate')))
        channels = self.config.get_param('active_channels')
        device_no = self.config.get_param('device_index')
        args = [exe, "-h" , str(host), '-p', str(port), '-v', v, "-d", simple_driver,
                    '-s', str(rate), '-c', channels, '-i', device_no]
        print args
        return args

if __name__ == "__main__":

    srv = AmplifierGtec(settings.MULTIPLEXER_ADDRESSES)
    srv.do_sampling()
