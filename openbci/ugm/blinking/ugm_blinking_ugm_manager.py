#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ugm import ugm_config_manager
class SingleUgmManager(object):
    def __init__(self, configs):
        mgr = ugm_config_manager.UgmConfigManager(configs['UGM_CONFIG'])
        start_id = int(configs['BLINK_UGM_ID_START'])
        count = int(configs['BLINK_UGM_ID_COUNT'])
        dec_count = int(configs['BLINK_ID_COUNT'])
        assert(start_id >= 0)
        assert(count >= 0)
        assert(count == dec_count)

        self.blink_ugm = []
        self.unblink_ugm = []

        for dec in range(count):
            cfg = mgr.get_config_for(start_id+dec)
            new_blink_cfg = {'id':cfg['id'],
                             configs['BLINK_UGM_KEY']:configs['BLINK_UGM_VALUE']
                             }
            new_unblink_cfg ={'id':cfg['id'],
                              configs['BLINK_UGM_KEY']:cfg['color']
                             }

            self.blink_ugm.append([new_blink_cfg])
            self.unblink_ugm.append([new_unblink_cfg])

    def get_blink_ugm(self, area_id):
        return self.blink_ugm[area_id]

    def get_unblink_ugm(self, area_id):
        return self.unblink_ugm[area_id]


class ClassicUgmManager(object):
    """Assumed that eg for:
    - blink_id_start = 10
    - blink_id_count = 8
    - row_count = 2
    - col_count = 4
    - we have matrix like:
    10 11 12 13
    14 15 16 17

    and decision 0,1,2,3 regard cols, decision 4,5 regard rows
    """
    def __init__(self, configs):
        mgr = ugm_config_manager.UgmConfigManager(configs['UGM_CONFIG'])
        start_id = int(configs['BLINK_UGM_ID_START'])
        count = int(configs['BLINK_UGM_ID_COUNT'])
        dec_count = int(configs['BLINK_ID_COUNT'])
        rows = int(configs['BLINK_UGM_ROW_COUNT'])
        cols = int(configs['BLINK_UGM_COL_COUNT'])
        assert(start_id >= 0)
        assert(count >= 0)
        assert(rows >= 0)
        assert(cols >= 0)
        assert(count == rows * cols)
        assert(dec_count >= 0)
        assert(dec_count == rows + cols)

        self.blink_ugm = []
        self.unblink_ugm = []

        for dec in range(dec_count):
            if dec < cols:
                blink_cfgs = []
                unblink_cfgs = []
                for row in range(rows):
                    cfg = mgr.get_config_for(start_id+row*cols+dec)
                    new_blink_cfg = {'id':cfg['id'],
                                     configs['BLINK_UGM_KEY']:configs['BLINK_UGM_VALUE']
                                     }
                    blink_cfgs.append(new_blink_cfg)
                    new_unblink_cfg ={'id':cfg['id'],
                                      configs['BLINK_UGM_KEY']:cfg['color']
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
                                     configs['BLINK_UGM_KEY']:configs['BLINK_UGM_VALUE']
                                     }
                    blink_cfgs.append(new_blink_cfg)
                    new_unblink_cfg ={'id':cfg['id'],
                                      configs['BLINK_UGM_KEY']:cfg['color']
                                      }
                    unblink_cfgs.append(new_unblink_cfg)
                self.blink_ugm.append(blink_cfgs)
                self.unblink_ugm.append(unblink_cfgs)


    def get_blink_ugm(self, area_id):
        return self.blink_ugm[area_id]

    def get_unblink_ugm(self, area_id):
        return self.unblink_ugm[area_id]
    


MGRS = {
    'SINGLE':SingleUgmManager,
    'CLASSIC':ClassicUgmManager
}

class UgmBlinkingUgmManager(object):
    def get_requested_configs(self):
        return ['UGM_CONFIG', 'BLINK_UGM_TYPE', 'BLINK_UGM_KEY', 'BLINK_UGM_VALUE', 'BLINK_UGM_ROW_COUNT', 'BLINK_UGM_COL_COUNT', 'BLINK_UGM_ID_START', 'BLINK_UGM_ID_COUNT', 'BLINK_ID_COUNT']

    def set_configs(self, configs):
        self._type = configs['BLINK_UGM_TYPE']
        self.configs = configs
        self.reset()

    def reset(self):
        self._mgr = MGRS[self._type](self.configs)

    def get_blink_ugm(self, area_id):
        return self._mgr.get_blink_ugm(area_id)

    def get_unblink_ugm(self, area_id):
        return self._mgr.get_unblink_ugm(area_id)
