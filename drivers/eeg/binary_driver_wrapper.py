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
SEP = ';'

class BinaryDriverWrapper(ConfiguredMultiplexerServer):
    desc_params = dict(amplifier_name='name',
                        physical_channels_no='physical_channels',
                        sampling_rates='sampling_rates',
                        channels_info='channels')

    def __init__(self, addresses, type):
        super(BinaryDriverWrapper, self).__init__(addresses=addresses, type=type)

        self._mx_addresses = addresses
        self.driver = self.run_driver()

        signal.signal(signal.SIGTERM, self.signal_handler())
        signal.signal(signal.SIGINT, self.signal_handler())

        desc = self.get_driver_description()
        print(desc)

        self.store_driver_description(desc)

        self.set_driver_params()
        self.ready()
        autostart = self.config.true_val(self.config.get_param('start_sampling'))
        LOGGER.info('Automatic start' + str(autostart))
        if autostart:
            self.start_sampling()
    
    def signal_handler(self):
        def handler(signum, frame):
            LOGGER.info("Got signal " + str(signum) + "!!! Stopping driver!")
            self.stop_sampling()
            sys.exit(-signum)
        return handler

    def run_driver(self):
        args=self.get_run_args(self._mx_addresses[0])
        LOGGER.info("Executing: "+' '.join(args))
        return Popen(args,stdin=subprocess.PIPE,stdout=subprocess.PIPE)

    def get_driver_description(self):
        return self._communicate()

# {    "name":"Porti7-24e4b4at",
#    "physical_channels": 34,
#    "sampling_rates":[128,256,512,1024,2048],
#    "channels": [        
                        # {"name": "ExG1", 
                        #     "gain": 1.0167751312255859e+00, 
                        #     "offset": -1.3535621337890625e+03,
                        #     "a": 7.1500003337860107e-02, 
                        #     "b": 0.0000000000000000e+00, 
                        #     "idle": -2147483648, 
                        #     "type": "EXG ", 
                        #     "unit": "Volt -6"}
#                    ]
#}

    def store_driver_description(self, driver_output):
        amp_desc=json.loads(driver_output)
        for par, desc_par in self.desc_params.iteritems():
            self.config.set_param(par, amp_desc[desc_par])
        self._extract_active_channels_info(amp_desc['channels'])

    def _extract_active_channels_info(self, channels_list):
        active = self.get_param('active_channels').split(SEP)
        names = self.get_param('channel_names').split(SEP)
        gains = []
        offsets = []
        if len(active) != len(names):
            LOGGER.error("Active channels list length different than channel names length!")
            self.stop_sampling()
            sys.exit(1)
        for chan in active:
            info = self._find_channel_info(chan, channels_list)
            gains.append(info['gain'])
            offsets.append(info['offset'])

        gains_str = SEP.join([str(g) for g in gains])
        offset_str = SEP.join([str(o) for o in offsets])
        self.set_param('channel_gains',  gains_str)
        self.set_param('channel_offsets', offset_str)
        LOGGER.info('Set active channels: ' + str(active) + ', channel_gains: ' +\
                                gains_str + ', channel_offsets: ' + offset_str)


    def _find_channel_info(self, chan, channels_list):
        match = [info for index, info in enumerate(channels_list) if \
                                                    info['name'] == chan or \
                                                    str(index) == chan]
        if not match:
            LOGGER.error('Invalid channel name ' + chan)
            self.stop_sampling()
            sys.exit(1)
        elif len(match) > 1:
            LOGGER.error('Ambiguous channel name ' + chan + str(channels_list))
            self.stop_sampling()
            sys.exit(1)
        
        return match.pop()

    def set_driver_params(self):
        self.set_sampling_rate(self.config.get_param("sampling_rate"))
        self.set_active_channels(self.config.get_param("active_channels"))

    def get_run_args(self,multiplexer_address):

        host,port=multiplexer_address
        exe=self.config.get_param('driver_executable')
        exe=os.path.join(obci_root(), exe)
        v=self.config.get_param('samples_per_packet')

        args=[exe,"-h",str(host),'-p',str(port),'-v', v]

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
        # sys.stderr.write("stop sampling")
        LOGGER.info("Stop sampling")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.driver.send_signal(signal.SIGINT)
        self.driver.wait()
        LOGGER.info("Sampling stopped")

    def driver_is_running(self):
        self.driver.poll()
        return self.driver.returncode is None

    def _communicate(self,command=""):
        if not self.driver_is_running():
            LOGGER.error("Driver is not running!!!!!!!")
            sys.exit(self.driver.returncode)

        out=""
        self.driver.stdin.write(command+"\n")
        while True:
            line=self.driver.stdout.readline()
            if len(line) == 0:
                LOGGER.error("Got empty string from driver. ABORTING...!!!")
                sys.exit(1)
            elif line=="\n": break

            out+=line;
        return out

    def handle_message(self, mxmsg):
        # handle something
        self.no_response()

    def validate_params(self, params, amp_params_received=False):
        if amp_params_received:
            for par in params:
                if params[par] == '':
                    LOGGER.error('Parameter ' + par + 'is empty!!! ABORTING....')
                    sys.exit(1)



if __name__ == "__main__":
    pass
    # import settings as settings
    # print signal.getsignal(signal.SIGINT)
    # srv = DriverWrapper(settings.MULTIPLEXER_ADDRESSES)
    # srv.do_sampling()
