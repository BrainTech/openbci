#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from ugm import ugm_config_manager
class EtrManager(object):
    def __init__(self):
        self.ugm_update_message = [
            """{'id':30000,
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
             'feedback_level':0}"""
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
