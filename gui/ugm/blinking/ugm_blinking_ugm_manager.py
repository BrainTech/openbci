#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

from ugm import ugm_config_manager
class _SingleUgmManager(object):
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
                              configs['BLINK_UGM_KEY']:cfg[configs['BLINK_UGM_KEY']]
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
                                      configs['BLINK_UGM_KEY']:cfg[configs['BLINK_UGM_KEY']]
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
                                      configs['BLINK_UGM_KEY']:cfg[configs['BLINK_UGM_KEY']]
                                      }
                    unblink_cfgs.append(new_unblink_cfg)
                self.blink_ugm.append(blink_cfgs)
                self.unblink_ugm.append(unblink_cfgs)


    def get_blink_ugm(self, area_id):
        return self.blink_ugm[area_id]

    def get_unblink_ugm(self, area_id):
        return self.unblink_ugm[area_id]
    


MGRS = {
    'SINGLE':_SingleUgmManager,
    'CLASSIC':_ClassicUgmManager
}

class UgmBlinkingUgmManager(object):
    """Provides effectively ugm configs for 'blinks' and 'unblinks'."""
    def get_requested_configs(self):
        return ['UGM_CONFIG', #ugm config name

                # Used by UgmBlinkingCountManager to generate blink ids. For given blink id, 
                # UgmBlinkingUgmManager should be able to return suitable ugm configs.
                # BLINK_ID_COUNT indicates that id will be in range [0;BLINK_ID_COUNT]
                'BLINK_ID_COUNT',

                # Blinker type, possible values:
                # SINGLE - every time one choosen field performs blink
                # CLASSIC - matrix-like blinker - blinks the whole row or whole column
                'BLINK_UGM_TYPE', 
                'BLINK_UGM_ROW_COUNT', # A number of rows in CLASSIC blinker
                'BLINK_UGM_COL_COUNT', # A number of cols in CLASSIC blinker
                # We should have always: BLINK_ID_COUNT == BLINK_UGM_ROW_COUNT + BLINK_UGM_COL_COUNT
                # We should have always: BLINK_UGM_ID_COUNT == BLINK_UGM_ROW_COUNT * BLINK_UGM_COL_COUNT
                # IN SINGLE blinker we whould have always: BLINK_UGM_ID_COUNT == BLINK_ID_COUNT

                # Start id and count of ugm components that are considered 'blinking' elements
                # It is assumed that to-be-blinked components are enumerated sequentially, eg. from 101 to 106 -
                # - then BLINK_UGM_ID_START would be 101, BLINK_UGM_COL_COUNT would be 5
                'BLINK_UGM_ID_START', 
                'BLINK_UGM_ID_COUNT', 

                # What property (KEY) and how (VALUE) should be changed on blink.
                # Eg. BLINK_UGM_KEY migh be 'color' and BLINK_UGM_VALUE migt be '#ff0000'
                'BLINK_UGM_KEY', 
                'BLINK_UGM_VALUE'
                ]

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
