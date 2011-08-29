#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
class EtrDecManager(object):
    def __init__(self):
        self.configs = {
            'SPELLER_AREA_COUNT': None,
            'ETR_BUFFER_SIZE': None
            }
    def get_requested_configs(self):
        return self.configs.keys()

    def set_configs(self, configs):
        for k in self.configs.keys():
            self.configs[k] = configs[k] #assumed all keys in self.configs are in configs
        self._assert_configs()
        self._init_configs()

    def _assert_configs(self):
        """Fired after setting configs from system settings.
        Assure configs are correct, change config type if needed 
        (system setting are always as strings)."""
        self.configs['SPELLER_AREA_COUNT'] = int(self.configs['SPELLER_AREA_COUNT'])
        assert(self.configs['SPELLER_AREA_COUNT'] > 0)

    def _init_configs(self):
        """Fired after set_configs,
        init all needed data structures."""
        pass

    def get_feedbacks(self, msg):
        """Fired every frame. Determine if (msg.x, msg.y) denotes 'moved'.
        Returns:
        - dec - decision (eg. if you have four decisions return 0 or 1 or 2 or 3 or -1(if no decision is made)
        - feeds - a list of floats in range [0;1] - 0 will result in no change in ugm, 1 will result in change
        of field`s colour. You should return '1' smartly - eg. if in time point T you return eg decision=2 then eg. for 
        5 subseqent time points (T+1, T+2 ...) you should return feeds like [0,0,1,0,0,0,...] so that user sees
        for at least few frames that he made a decision"""
        dec = -1
        feeds = [0]*self.configs['SPELLER_AREA_COUNT']
        
        #update some local data structures if you want
        #change dec if you want
        # update feeds if you want
        return dec, feeds
