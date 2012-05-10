#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from multiplexer.multiplexer_constants import peers, types
from peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from drivers import drivers_logging as logger
from drivers.eeg.driver_comm import DriverComm
from configs import settings

import json

LOGGER = logger.get_logger("BinaryDriverWrapper", "info")
SEP = ';'

class BinaryDriverWrapper(ConfiguredMultiplexerServer, DriverComm):
    """A wrapper around c++ amplifier binaries with INI configuration support.
    """
    desc_params = dict(amplifier_name='name',
                        physical_channels_no='physical_channels',
                        sampling_rates='sampling_rates',
                        channels_info='channels')

    def __init__(self, addresses, type):
        super(BinaryDriverWrapper, self).__init__(addresses=addresses, type=type)
        self._mx_addresses = addresses
        DriverComm.__init__(self, self.config, addresses)
        self._run_post_super()

        desc = self.get_driver_description()
        # print(desc)
        if desc.startswith('DEVICE OPEN ERROR'):
            self.abort("DEVICE PROBLEM: " + desc + " ...ABORTING!!!")

        self.store_driver_description(desc)

        autostart = self.config.true_val(self.config.get_param('start_sampling'))

        self.ready()

        LOGGER.info('Automatic start' + str(autostart))
        if autostart:
            self.set_driver_params()
            self.start_sampling()

    def _run_post_super(self):
        pass

    def store_driver_description(self, driver_output):
        if len(driver_output) < 500:
            LOGGER.info("This does not look good: "+driver_output)
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
                    LOGGER.error('Parameter ' + par + 'is empty!!! ABORTING....')
                    sys.exit(1)


if __name__ == "__main__":
    pass
    # import settings as settings

    # srv = BinaryDriverWrapper(settings.MULTIPLEXER_ADDRESSES)
   
