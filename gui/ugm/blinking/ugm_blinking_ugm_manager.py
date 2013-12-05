#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

from obci.gui.ugm import ugm_config_manager
class _SingleUgmManager(object):
    def __init__(self, configs):
        mgr = ugm_config_manager.UgmConfigManager(configs.get_param('ugm_config'))
        start_id = int(configs.get_param('blink_ugm_id_start'))
        count = int(configs.get_param('blink_ugm_id_count'))
        dec_count = int(configs.get_param('blink_id_count'))
        active_field_ids = [int(field) for field in configs.get_param('active_field_ids').split(';')]
    
        assert(start_id >= 0)
        assert(count >= 0)
        #assert(count == dec_count)

        self.blink_ugm = []
        self.unblink_ugm = []
        for dec in active_field_ids:#range(count):
            cfg = mgr.get_config_for(start_id+dec)
            new_blink_cfg = {'id':cfg['id'],
                             configs.get_param('blink_ugm_key'):configs.get_param('blink_ugm_value')
                             }
            new_unblink_cfg ={'id':cfg['id'],
                              configs.get_param('blink_ugm_key'):cfg[configs.get_param('blink_ugm_key')]
                              }
            self.blink_ugm.append([new_blink_cfg])
            self.unblink_ugm.append([new_unblink_cfg])

    def get_blink_ugm(self, area_id):
        return self.blink_ugm[area_id]

    def get_unblink_ugm(self, area_id):
        return self.unblink_ugm[area_id]


class _ClassicUgmManager(object):
    """Assumed that eg for:
    - blink_ugm_id_start = 10
    - blink_ugm_id_count = 8
    - row_count = 2
    - col_count = 4
    - we have matrix like:
    10 11 12 13
    14 15 16 17
    and decision 0,1,2,3 regard cols, decision 4,5 regard rows.
    As a result returned ugm for eg. decision 4 contains a list of ugm configs
    for every field in the second row.
    """
    def __init__(self, configs):
        mgr = ugm_config_manager.UgmConfigManager(configs.get_param('ugm_config'))
        start_id = int(configs.get_param("blink_ugm_id_start"))
        count = int(configs.get_param('blink_ugm_id_count'))
        dec_count = int(configs.get_param('blink_id_count'))
        dec_start = int(configs.get_param('blink_id_start'))
        rows = int(configs.get_param('blink_ugm_row_count'))
        cols = int(configs.get_param('blink_ugm_col_count'))
        assert(start_id >= 0)
        assert(count >= 0)
        assert(rows >= 0)
        assert(cols >= 0)
        #assert(count == rows * cols)
        assert(dec_count >= 0)
        #assert(dec_count == rows + cols)

        self.blink_ugm = []
        self.unblink_ugm = []

        for dec in range(dec_start+dec_count):
            if dec < cols:
                blink_cfgs = []
                unblink_cfgs = []
                for row in range(rows):
                    cfg = mgr.get_config_for(start_id+row*cols+dec)
                    new_blink_cfg = {'id':cfg['id'],
                                     configs.get_param('blink_ugm_key'):configs.get_param('blink_ugm_value')
                                     }
                    blink_cfgs.append(new_blink_cfg)
                    new_unblink_cfg ={'id':cfg['id'],
                                      configs.get_param('blink_ugm_key'):cfg[configs.get_param('blink_ugm_key')]
                                      }
                    unblink_cfgs.append(new_unblink_cfg)
                self.blink_ugm.append(blink_cfgs)
                self.unblink_ugm.append(unblink_cfgs)
            else:
                dc = dec - cols
                blink_cfgs = []
                unblink_cfgs = []
                for col in range(cols):
                    cfg = mgr.get_config_for(start_id+cols*dc + col)
                    new_blink_cfg = {'id':cfg['id'],
                                     configs.get_param('blink_ugm_key'):configs.get_param('blink_ugm_value')
                                     }
                    blink_cfgs.append(new_blink_cfg)
                    new_unblink_cfg ={'id':cfg['id'],
                                      configs.get_param('blink_ugm_key'):cfg[configs.get_param('blink_ugm_key')]
                                      }
                    blink_cfgs.append(new_blink_cfg)
                    unblink_cfgs.append(new_unblink_cfg)

                self.blink_ugm.append(blink_cfgs)
                self.unblink_ugm.append(unblink_cfgs)


    def get_blink_ugm(self, area_id):
        return self.blink_ugm[area_id]

    def get_unblink_ugm(self, area_id):
        return self.unblink_ugm[area_id]
    


MGRS = {
    'single':_SingleUgmManager,
    'classic':_ClassicUgmManager
}

class UgmBlinkingUgmManager(object):
    """Provides effectively ugm configs for 'blinks' and 'unblinks'."""

    def set_configs(self, configs):
        self._type = configs.get_param('blink_ugm_type')
        self.configs = configs
        self.reset()

    def reset(self):
        self._mgr = MGRS[self._type](self.configs)

    def get_blink_ugm(self, area_id):
        return self._mgr.get_blink_ugm(area_id)

    def get_unblink_ugm(self, area_id):
        return self._mgr.get_unblink_ugm(area_id)
