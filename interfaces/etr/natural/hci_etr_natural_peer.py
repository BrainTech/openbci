#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random, time, sys

from configs import settings, variables_pb2
from gui.ugm import ugm_helper
from interfaces.etr import hci_etr
from interfaces.etr.natural import etr_natural_dec_manager
from interfaces.etr import etr_ugm_manager
from interfaces import interfaces_logging as logger
LOGGER = logger.get_logger("hci_etr_classic", "info")

class HciEtrNatural(hci_etr.HciEtr):
    def __init__(self, addresses):
        super(HciEtrNatural, self).__init__(addresses=addresses)

        self.dec_mgr = etr_natural_dec_manager.EtrDecManager(
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
        LOGGER.debug("Got etr msg: "+str(msg))
        
        msg = self.dec_mgr.getRealData(msg)
        
        area_id = self.ugm_mgr.get_pushed_area_id(msg)
        self.dec_mgr.area_pushed(area_id, msg)
        
        dec, feeds = self.dec_mgr.get_feedbacks()
        ugms = self.ugm_mgr.get_ugm_updates(feeds, msg)
        
        return dec, ugms
        
    def handle_calibration_mesage(self, msg):
        """
        Handles massage that informs when was calibration processed.
        """
        LOGGER.debug("Got etr msg: "+str(msg))
        #### What to do when receive ETR_MATRIX information
        res = variables_pb2.Sample()
        res.ParseFromString(msg)
        LOGGER.debug("GOT ETR CALIBRATION RESULTS: "+str(res.channels))
        self.dec_mgr.updateTransformationMatrix(res.channels)

if __name__ == "__main__":
    HciEtrNatural(settings.MULTIPLEXER_ADDRESSES).loop()
