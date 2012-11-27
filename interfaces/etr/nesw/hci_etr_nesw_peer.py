#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random, time, sys

from obci_configs import settings, variables_pb2
from gui.ugm import ugm_helper
from interfaces.etr import hci_etr
from interfaces.etr.nesw import etr_nesw_dec_manager
from interfaces.etr import etr_ugm_manager

class HciEtrNESW(hci_etr.HciEtr):
    def __init__(self, addresses):
        super(HciEtrNESW, self).__init__(addresses=addresses)
        self.dec_mgr = etr_nesw_dec_manager.EtrDecManager(
            self.get_param('speller_area_count'),
            self.get_param('buffer_size'),
            self.get_param('ratio'),
            self.get_param('stack'),
            self.get_param('delay'),
            self.get_param('dec_count'),
            self.get_param('feed_fade'),
	    self.get_param('long_dec_delay')
            )

        start_id = self.get_param('ugm_field_ids').split(';')[0]
        self.ugm_mgr = etr_ugm_manager.EtrUgmManager(
            self.get_param('ugm_config'),
            self.get_param('speller_area_count'),
            start_id,
            self.get_param('fix_id')
            )
        self.ready()

    def handle_etr_message(self, msg):
        dec, feeds = self.dec_mgr.get_feedbacks(msg)
        ugms = self.ugm_mgr.get_ugm_updates(feeds, msg)
        return dec, ugms

if __name__ == "__main__":
    HciEtrNESW(settings.MULTIPLEXER_ADDRESSES).loop()

