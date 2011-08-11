#!/usr/bin/env python
# -*- coding: utf-8 -*-
import etr_dec_manager
import etr_ugm_manager
class EtrManager(object):
    def __init__(self):
        self.dec_mgr = etr_dec_manager.EtrDecManager()
        self.ugm_mgr = etr_ugm_manager.EtrUgmManager()

    def get_requested_configs(self):
        return set(self.dec_mgr.get_requested_configs() + self.ugm_mgr.get_requested_configs())

    def set_configs(self, configs):
        self.dec_mgr.set_configs(configs)
        self.ugm_mgr.set_configs(configs)

    def handle_message(self, msg):
        area_id = self.ugm_mgr.get_pushed_area_id(msg)
        self.dec_mgr.area_pushed(area_id, msg)
        print("Area pushed: "+str(area_id))
        dec, feeds = self.dec_mgr.get_feedbacks()
        print("DEC AND FEED: "+str(dec)+ " / " + str(feeds))
        ugms = self.ugm_mgr.get_ugm_updates(feeds, msg)
        return dec, ugms










"""
    def __init__(self):
        self.ugm_update_message = [

{'id':30000,
             'feedback_level':0},
            {'id':30001,
             'feedback_level':0},
            {'id':30002,
             'feedback_level':0},
            {'id':30003,
             'feedback_level':0},
            {'id':30004,
             'feedback_level':0},
            {'id':30005,
             'feedback_level':0},
            {'id':30006,
             'feedback_level':0},
            {'id':30007,
             'feedback_level':0}
            {'id':12345,
             'position_horizontal':0.0,
             'position_vertical':0.0
}
]

        self.ugm_config_manager = ugm_config_manager.UgmConfigManager('feedback_speller_config3')
        print(self.ugm_config_manager.get_ugm_fields())

    def get_initial_ugm_config(self):
        return str(self.ugm_config_manager.get_ugm_fields())

    def handle_message(self, p_msg):
        #for i, msg_dict in enumerate(self.ugm_update_message):
        #    msg_dict['feedback_level'] = random.random()
        self.ugm_update_message[0]['position_vertical'] = random.random()
        self.ugm_update_message[0]['position_horizontal'] = random.random()
        return None, str(self.ugm_update_message)
"""
