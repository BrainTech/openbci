#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ugm import ugm_config_manager

class AreaConfig(object):
    def __init__(self, ugm_config):
        self.x1 = float(ugm_config['position_horizontal'])
        self.y1 = float(ugm_config['position_vertical'])
        self.x2 = self.x1 + float(ugm_config['width'])
        self.y2 = self.y1 + float(ugm_config['height'])

        self.config = {'id': ugm_config['id']}

    def get_ugm_update(self, feedback):
        self.config['color'] = '#%02x%02x%02x' % (255 - int(255*feedback), 255, 255 - int(255*feedback))
        return self.config


class FixConfig(object):
    def __init__(self, ugm_config):
        self.config = {'id': ugm_config['id'],
                       'width':ugm_config['width'],
                       'height':ugm_config['height']
                       }

    def get_ugm_update(self, msg):
        self.config['position_horizontal'] = (1-msg.x) - float(self.config['width'])/2
        self.config['position_vertical'] = msg.y - float(self.config['height'])/2
        return self.config

class EtrUgmManager(object):
    def __init__(self):
        self.configs = {
            'UGM_CONFIG': None,
            'SPELLER_AREA_COUNT': None,
            'ETR_START_AREA_ID': None,
            'ETR_FIX_ID': None
            }

    def get_requested_configs(self):
        return self.configs.keys()

    def set_configs(self, configs):
        for k in self.configs.keys():
            self.configs[k] = configs[k] #assumed all keys in self.configs are in configs
        self._assert_configs()
        self._init_configs()

    def _assert_configs(self):
        self.configs['SPELLER_AREA_COUNT'] = int(self.configs['SPELLER_AREA_COUNT'])
        self.configs['ETR_START_AREA_ID'] = int(self.configs['ETR_START_AREA_ID'])
        self.configs['ETR_FIX_ID'] = int(self.configs['ETR_FIX_ID'])
        assert(self.configs['SPELLER_AREA_COUNT'] > 0)

    def _init_configs(self):
        mgr = ugm_config_manager.UgmConfigManager(self.configs['UGM_CONFIG'])

        self.area_configs = []
        count = self.configs['ETR_START_AREA_ID']
        for i in range(self.configs['SPELLER_AREA_COUNT']):
            self.area_configs.append(AreaConfig(mgr.get_config_for(count+i)))

        self.fix_config = FixConfig(mgr.get_config_for(self.configs['ETR_FIX_ID']))
                                    

    def get_pushed_area_id(self, msg):
        for i, p in enumerate(self.area_configs):
            if p.x1 <= (1-msg.x) and (1-msg.x) <= p.x2 and p.y1 <= msg.y and msg.y <= p.y2:
                return i
        return -1

    def get_ugm_updates(self, feeds, msg):
        updates = []
        for i in range(len(feeds)):
            if feeds[i] > 0:
                updates.append(self.area_configs[i].get_ugm_update(feeds[i]))
        updates.append(self.fix_config.get_ugm_update(msg))

        return str(updates)
        
