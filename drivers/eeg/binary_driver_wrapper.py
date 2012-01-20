#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os.path
import subprocess
import signal

from multiplexer.multiplexer_constants import peers, types
from peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from drivers import drivers_logging as logger
from configs import settings
from launcher.launcher_tools import obci_root

from subprocess import Popen
import json

# set params
# get description
# store description
# run command
#start sampling
# stop sampling
LOGGER = logger.get_logger("BinaryDriverWrapper", "info")

class BinaryDriverWrapper(ConfiguredMultiplexerServer):
    desc_params = dict(amplifier_name='name',
                        physical_channels_no='physical_channels',
                        sampling_rates='sampling_rates',
                        channels='channels')

    def __init__(self, addresses, type):
        super(BinaryDriverWrapper, self).__init__(addresses=addresses, type=type)
        self._mx_addresses = addresses
        self.driver = self.run_driver()
        print("AAAASIA")
        desc = self.get_driver_description()
        print(desc)
        print("MAAATI")
        self.store_driver_description(desc)

        self.set_driver_params()
        self.ready()
        autostart = self.config.true_val(self.config.get_param('start_sampling'))
        LOGGER.info('Automatic start' + str(autostart))
        if autostart:

            self.start_sampling()

    def run_driver(self):
        args=self.get_run_args(self._mx_addresses[0])
        LOGGER.info("Executing: "+' '.join(args))
        return Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE)

    def get_driver_description(self):
        return self._communicate()

    def store_driver_description(self, driver_output):
        amp_desc=json.loads(driver_output)
        for par, desc_par in self.desc_params.iteritems():
            self.config.set_param(par, amp_desc[desc_par])

    def set_driver_params(self):
        self.set_sampling_rate(self.config.get_param("sampling_rate"))
        self.set_active_channels(self.config.get_param("active_channels"))

    def get_run_args(self,multiplexer_address):

        host,port=multiplexer_address
        exe=self.config.get_param('driver_executable')
        exe=os.path.join(obci_root(), exe)
        args=[exe,"-h",str(host),'-p',str(port)]

        if self.config.get_param("usb_device"):
            args.extend(["-d",self.config.get_param("usb_device")])
        elif self.config.get_param("bluetooth_device"):
            args.extend(["-b",self.config.get_param("bluetooth_device")])
        else:
            raise Exception("usb_device or bluetooth_device is required")
        if self.config.get_param("amplifier_responses"):
            args.extend(["-r", self.config.get_param("amplifier_responses")])
        if self.config.get_param("dump_responses"):
            args.extend(["--save_responses", self.config.get_param("dump_responses")])
        return args

    def do_sampling(self):
        self.driver.wait()
        LOGGER.info("Driver finished working with code " + str(self.driver.returncode))
        sys.exit(self.driver.returncode)

    def set_sampling_rate(self,sampling_rate):
        LOGGER.info("Set sampling rate: %s "%sampling_rate)
        error=self._communicate("sampling_rate "+str(sampling_rate))
        if error:
            print error

    def set_active_channels(self,active_channels):
        LOGGER.info("Set Active channels: %s"%active_channels)
        error=self._communicate("active_channels "+str(active_channels))
        if error:
            print error

    def start_sampling(self):
        signal.signal(signal.SIGINT, self.stop_sampling)
        LOGGER.info("Start sampling")
        error=self._communicate("start")
        if error:
            print error
        LOGGER.info("Sampling started")

    def stop_sampling(self,_1=None,_2=None):
        sys.stderr.write("stop sampling")
        LOGGER.info("Stop sampling")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.driver.send_signal(signal.SIGINT)
        LOGGER.info("Sampling stopped")

    def _communicate(self,command=""):
        self.driver.poll()
        if self.driver.returncode is not None:
            raise Exception("Driver is not running!!!!!!!")
        out=""
        self.driver.stdin.write(command+"\n")
        while True:
            line=self.driver.stdout.readline()
            if len(line) == 0:
                raise Exception("Got empty string from driver. Aborting!!!")
            elif line=="\n": break

            out+=line;
        return out

    def handle_message(self, mxmsg):
        # handle something
        self.no_response()

if __name__ == "__main__":
    pass
    # import settings as settings
    # print signal.getsignal(signal.SIGINT)
    # srv = DriverWrapper(settings.MULTIPLEXER_ADDRESSES)
    # srv.do_sampling()
