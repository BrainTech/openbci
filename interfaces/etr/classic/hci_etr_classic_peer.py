#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random, time, sys

from obci.configs import settings, variables_pb2
from obci.gui.ugm import ugm_helper
from obci.interfaces.etr import hci_etr
from obci.interfaces.etr.classic import etr_classic_dec_manager
from obci.interfaces.etr import etr_ugm_manager

class HciEtrClassic(hci_etr.HciEtr):
    def __init__(self, addresses):
        super(HciEtrClassic, self).__init__(addresses=addresses)

        self.dec_mgr = etr_classic_dec_manager.EtrDecManager(
            self.get_param('dec_type'),
            self.get_param('push_dec_count'),
            self.get_param('push_feed_count'),
            self.get_param('buffer_size'),
            self.get_param('ignore_missed'),
            self.get_param('speller_area_count'),
            self.get_param('dec_break')
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
        self.logger.debug("Got etr msg: "+str(msg))
        area_id = self.ugm_mgr.get_pushed_area_id(msg)
        self.dec_mgr.area_pushed(area_id, msg)
        dec, feeds = self.dec_mgr.get_feedbacks()
        ugms = self.ugm_mgr.get_ugm_updates(feeds, msg)
        return dec, ugms

if __name__ == "__main__":
    HciEtrClassic(settings.MULTIPLEXER_ADDRESSES).loop()
