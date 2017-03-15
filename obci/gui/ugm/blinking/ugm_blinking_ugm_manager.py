#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>

from obci.gui.ugm import ugm_config_manager
import os.path
class _SingleUgmManager(object):
    def __init__(self, configs):
        mgr = ugm_config_manager.UgmConfigManager(configs.get_param('ugm_config'))
        start_id = int(configs.get_param('blink_ugm_id_start'))
        count = int(configs.get_param('blink_ugm_id_count'))
        dec_count = int(configs.get_param('blink_id_count'))
        active_field_ids = [int(field) for field in configs.get_param('active_field_ids').split(';')]
    
        assert(start_id >= 0)
        assert(count >= 0)
        assert(count == dec_count)

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
        rows = int(configs.get_param('blink_ugm_row_count'))
        cols = int(configs.get_param('blink_ugm_col_count'))
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
    


class _SingleTextImageOddballUgmManager(object):
    '''Ugm config manager for blinks - text with synchronous nontarget
    blinks and additional target oddball - image.
    
    BCI design maximising efficiency based on studies:
    Jin, Jing, et al. "A P300 Brain–Computer Interface Based on a
    Modification of the Mismatch Negativity Paradigm."
    International journal of neural systems 25.03 (2015): 1550011.
    
    Kaufmann, Tobias, et al. "Face stimuli effectively
    prevent brain–computer interface inefficiency in patients with
    neurodegenerative disease."
    Clinical Neurophysiology 124.5 (2013): 893-900.

    '''
    def __init__(self, configs):
        mgr = ugm_config_manager.UgmConfigManager(configs.get_param('ugm_config'))
        start_id = int(configs.get_param('blink_ugm_id_start'))
        count = int(configs.get_param('blink_ugm_id_count'))
        dec_count = int(configs.get_param('blink_id_count'))
        active_field_ids = [int(field) for field in configs.get_param('active_field_ids').split(';')]
        target_image_path = configs.get_param('target_image_path')
        image_fields_id_offset = int(configs.get_param('image_fields_id_offset'))
        
        assert(start_id >= 0)
        assert(count >= 0)
        assert(count == dec_count)

        self.blink_ugm = []
        self.unblink_ugm = []
        self.half_blink_ugm = []
        self.half_unblink_ugm = []
        #create blinks and unblinks for every field
        for dec in active_field_ids:#range(count):
            new_blink_cfgs = []
            new_unblink_cfgs = []
            cfg_target = mgr.get_config_for(start_id+dec+image_fields_id_offset)
            new_blink_cfgs.append({'id':cfg_target['id'],
                                 'image_path':target_image_path
                                 })
            new_unblink_cfgs.append({'id':cfg_target['id'],
                                 'image_path':''
                                 })
            #highlight every nontarget field:
            
            for ndec in active_field_ids:
                cfg = mgr.get_config_for(start_id+ndec)
                half_blink = {'id':cfg['id'],
                             configs.get_param('blink_ugm_key'):configs.get_param('blink_ugm_value')
                                }
                new_blink_cfgs.append(half_blink)
                self.half_blink_ugm.append(half_blink)
                half_unblink = {'id':cfg['id'],
                            configs.get_param('blink_ugm_key'):cfg[configs.get_param('blink_ugm_key')]
                                }
                new_unblink_cfgs.append(half_unblink)
                self.half_unblink_ugm.append(half_unblink)
            self.blink_ugm.append(new_blink_cfgs)
            self.unblink_ugm.append(new_unblink_cfgs)
        #creating half blink
            

    def get_blink_ugm(self, area_id):
        if area_id is not None:
            return self.blink_ugm[area_id]
        else:
            return self.half_blink_ugm

    def get_unblink_ugm(self, area_id):
        if area_id is not None:
            return self.unblink_ugm[area_id]
        else:
            return self.half_unblink_ugm


class _SingleImageOddballUgmManager(_SingleTextImageOddballUgmManager):
    '''Ugm config manager for blinks - images with synchronous nontarget
    blinks and additional target oddball - image - another image.
    
    BCI design maximising efficiency based on studies:
    Jin, Jing, et al. "A P300 Brain–Computer Interface Based on a
    Modification of the Mismatch Negativity Paradigm."
    International journal of neural systems 25.03 (2015): 1550011.
    
    Kaufmann, Tobias, et al. "Face stimuli effectively
    prevent brain–computer interface inefficiency in patients with
    neurodegenerative disease."
    Clinical Neurophysiology 124.5 (2013): 893-900.

    '''
    def __init__(self, configs):
        mgr = ugm_config_manager.UgmConfigManager(configs.get_param('ugm_config'))
        start_id = int(configs.get_param('blink_ugm_id_start'))
        count = int(configs.get_param('blink_ugm_id_count'))
        dec_count = int(configs.get_param('blink_id_count'))
        active_field_ids = [int(field) for field in configs.get_param('active_field_ids').split(';')]
        images_folder = configs.get_param('images_path')
        images_extension = configs.get_param('images_extension')
        
        assert(start_id >= 0)
        assert(count >= 0)
        assert(count == dec_count)

        self.blink_ugm = []
        self.unblink_ugm = []
        self.half_unblink_ugm = []
        self.half_blink_ugm = []
        #create blinks and unblinks for every field
        for dec in active_field_ids:
            new_blink_cfgs = []
            new_unblink_cfgs = []
            
            cfg_target = mgr.get_config_for(start_id+dec)
            targ_image = os.path.join(images_folder,
                                    '{}t.{}'.format(dec, images_extension))
            idle_image = os.path.join(images_folder,
                                    '{}i.{}'.format(dec, images_extension))
            new_blink_cfgs.append({'id':cfg_target['id'],
                                 'image_path':targ_image
                                 })
            new_unblink_cfgs.append({'id':cfg_target['id'],
                                 'image_path':idle_image
                                 })
            #highlight every nontarget field:
            
            for ndec in active_field_ids:
                #change only nontarget, here this is important
                if ndec!=dec:
                    
                    high_image = os.path.join(images_folder,
                                    '{}n.{}'.format(ndec, images_extension))
                    idle_image = os.path.join(images_folder,
                                    '{}i.{}'.format(ndec, images_extension))
                    cfg = mgr.get_config_for(start_id+ndec)
                    new_blink_cfgs.append({'id':cfg['id'],
                                     'image_path':high_image
                                     })
                    new_unblink_cfgs.append({'id':cfg['id'],
                                      'image_path':idle_image
                                      })
                                      
            self.blink_ugm.append(new_blink_cfgs)
            self.unblink_ugm.append(new_unblink_cfgs)
        #creating half blinks:
        for ndec in active_field_ids:
            high_image = os.path.join(images_folder,
                            '{}n.{}'.format(ndec, images_extension))
            idle_image = os.path.join(images_folder,
                            '{}i.{}'.format(ndec, images_extension))
            cfg = mgr.get_config_for(start_id+ndec)
            self.half_blink_ugm.append({'id':cfg['id'],
                             'image_path':high_image
                             })
            self.half_unblink_ugm.append({'id':cfg['id'],
                              'image_path':idle_image
                              })


MGRS = {
    'single':_SingleUgmManager,
    'classic':_ClassicUgmManager,
    'singletextimageoddball':_SingleTextImageOddballUgmManager,
    'singleimageoddball':_SingleImageOddballUgmManager,
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
