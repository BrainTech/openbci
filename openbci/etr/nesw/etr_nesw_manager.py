#!/usr/bin/env python
# -*- coding: utf-8 -*-
import etr_nesw_dec_manager
from openbci.etr import etr_ugm_manager
class EtrNeswManager(object):
    def __init__(self):
        self.dec_mgr = etr_nesw_dec_manager.EtrDecManager()
        self.ugm_mgr = etr_ugm_manager.EtrUgmManager()

    def get_requested_configs(self):
        return set(self.dec_mgr.get_requested_configs() + self.ugm_mgr.get_requested_configs())

    def set_configs(self, configs):
        self.dec_mgr.set_configs(configs)
        self.ugm_mgr.set_configs(configs)

    def handle_message(self, msg):
        dec, feeds = self.dec_mgr.get_feedbacks(msg)
        ugms = self.ugm_mgr.get_ugm_updates(feeds, msg)
        return dec, ugms
