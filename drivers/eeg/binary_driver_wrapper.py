#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.drivers.eeg.driver_comm import DriverComm
from obci.configs import settings
from obci.utils import context as ctx

import json

SEP = ';'

class BinaryDriverWrapper(ConfiguredMultiplexerServer, DriverComm):
    """A wrapper around c++ amplifier binaries with INI configuration support.
    """
    desc_params = dict(amplifier_name='name',
                        physical_channels_no='physical_channels',
                        sampling_rates='sampling_rates',
                        channels_info='channels')

    def __init__(self, addresses, type):
        """Do:
        1) run super constructor to receive configs
        2) run DriverComm constructor that fires binary driver
        3) get json description from the driver (desc_params are required)
        4) store that description in self.configs to share it with other modules
        5) if autostart is set to true: 
        6) set driver params from config (sampling_rate and active_channels)
        7) start sampling
        """
        super(BinaryDriverWrapper, self).__init__(addresses=addresses, type=type)
        self._init_got_configs()
        self._mx_addresses = addresses
        context = ctx.get_new_context()
        context['logger'] = self.logger
        DriverComm.__init__(self, self.config, addresses, context)

        desc = self.get_driver_description()
        if desc.startswith('DEVICE OPEN ERROR'):
            self.abort("DEVICE PROBLEM: " + desc + " ...ABORTING!!!")
        self.store_driver_description(desc)

        autostart = self.config.true_val(self.config.get_param('start_sampling'))
        self.logger.info('Automatic start' + str(autostart))

        self.ready()
        if autostart:
            self.set_driver_params()
            self.start_sampling()

    def _init_got_configs(self):
        pass

    def store_driver_description(self, driver_output):
        if len(driver_output) < 500:
            self.logger.info("This does not look good: "+driver_output)
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
            self.logger.error("Active channels list length different than channel names length!")
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
        self.logger.info('Set active channels: ' + str(active) + ', channel_gains: ' +\
                                gains_str + ', channel_offsets: ' + offset_str)


    def _find_channel_info(self, chan, channels_list):
        match = [info for index, info in enumerate(channels_list) if \
                                                    info['name'] == chan or \
                                                    str(index) == chan]
        if not match:
            self.logger.error('Invalid channel name ' + chan)
            self.stop_sampling()
            sys.exit(1)
        elif len(match) > 1:
            self.logger.error('Ambiguous channel name ' + chan + str(channels_list))
            self.stop_sampling()
            sys.exit(1)

        return match.pop()

    def abort(self, error_msg):
        self.set_param('error_details', error_msg)
        DriverComm.abort(self, error_msg)
        
    def handle_message(self, mxmsg):
        # handle something
        self.no_response()

    def validate_params(self, params, amp_params_received=False):
        if amp_params_received:
            for par in params:
                if params[par] == '':
                    self.logger.error('Parameter ' + par + 'is empty!!! ABORTING....')
                    sys.exit(1)


if __name__ == "__main__":
    pass
    # import settings as settings

    # srv = BinaryDriverWrapper(settings.MULTIPLEXER_ADDRESSES)
   
