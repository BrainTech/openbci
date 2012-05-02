#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gui.ugm import ugm_config_manager

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
                       'height':ugm_config['height'],
                       'color':ugm_config['color']
                       }
        self.normal_color = self.config['color']
        c = str(self.normal_color[1:])
        r, g, b = c[:2], c[2:4], c[4:]
        rgb = tuple([int(n, 16) for n in (r, g, b)])
        self.out_color = '#%02x%02x%02x' % (255-rgb[0], 255-rgb[1], 255-rgb[2])
        self.width = float(self.config['width'])
        self.height = float(self.config['height'])

    def get_ugm_update(self, msg):
        x = (1-msg.x)-self.width/2
        y = msg.y-self.height/2
        out = False
        if x < 0:
            out = True
            x = 0.0
        elif x > 1:
            out = True
            x = 1.0-self.width
        if y < 0:
            out = True
            y = 0.0
        elif y > 1:
            out = True
            y = 1.0-self.height
        if out:
            self.config['color'] = self.out_color
        else:
            self.config['color'] = self.normal_color


        self.config['position_horizontal'] = x
        self.config['position_vertical'] = y
        return self.config

class EtrUgmManager(object):
    def __init__(self, ugm_config, speller_area_count, start_area_id, fix_id):
        self.speller_area_count = int(speller_area_count)
        self.start_area_id = int(start_area_id)
        self.fix_id = int(fix_id)
        assert(self.speller_area_count > 0)
        mgr = ugm_config_manager.UgmConfigManager(ugm_config)
        self.area_configs = []
        count = self.start_area_id
        for i in range(self.speller_area_count):
            print("GOOOO: "+str(count+i))
            self.area_configs.append(AreaConfig(mgr.get_config_for(count+i)))

        self.fix_config = FixConfig(mgr.get_config_for(self.fix_id))
                                    

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
        
