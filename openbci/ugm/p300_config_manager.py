#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ugm_config_manager
import copy

class P300ConfigManager(object):
    def __init__(self):
        pass
    def get_blink_row(self, row):
        return self.blink_rows[row], self.non_blink_rows[row]
    def get_blink_col(self, col):
        return self.blink_cols[col], self.non_blink_cols[col]

    def generate_config(self, rows, cols, sq_size, font_size, letters, blink_mode):
        mgr = ugm_config_manager.UgmConfigManager('p300_base')
        top = mgr.get_config_for(888)
        bot = mgr.get_config_for(999)
        base = mgr.get_config_for(1)
        stims = self._generate_speller_stims(base, rows, cols, sq_size, '#000000', font_size, letters)
        bot['stimuluses'] = stims
        mgr.set_full_config([top, bot])
        #mgr.update_to_file('5_5_p300', True)
        self._set_blinks(mgr, rows, cols, blink_mode, '#ffffff')
        return [top, bot]


    def _set_blinks(self, mgr, rows, cols, blink_mode, blink_color):
        self.blink_rows = []
        self.blink_cols = []
        self.non_blink_rows = []
        self.non_blink_cols = []
        
        for i_row in range(rows):
            blink_row = []
            non_blink_row = []
            for j_col in range(cols):
                stim_id = self._get_stim_id_for(i_row, j_col, rows, cols, blink_mode)
                stim = mgr.get_config_for(stim_id)
                non_blink_row.append(stim)

                stim = mgr.get_config_for(stim_id)
                if blink_mode == 'letter':
                    stim['font_color'] = blink_color
                elif blink_mode == 'square':
                    stim['color'] = blink_color
                else:
                    raise Exception("An unknow stimulus type was requested!")
                blink_row.append(stim)
            self.blink_rows.append(blink_row)
            self.non_blink_rows.append(non_blink_row)
        
        for i_col in range(cols):
            blink_col = []
            non_blink_col = []
            for j_row in range(rows):
                stim_id = self._get_stim_id_for(j_row, i_col, rows, cols, blink_mode)
                stim = mgr.get_config_for(stim_id)
                non_blink_col.append(stim)

                stim = mgr.get_config_for(stim_id)
                if blink_mode == 'letter':
                    stim['font_color'] = blink_color
                elif blink_mode == 'square':
                    stim['color'] = blink_color
                else:
                    raise Exception("An unknow stimulus type was requested!")
                blink_col.append(stim)
            self.blink_cols.append(blink_col)
            self.non_blink_cols.append(non_blink_col)
        print([(r['id'], r['color']) for r in self.blink_rows[0]])
        print([(r['id'], r['color']) for r in self.non_blink_rows[0]])

    def _get_stim_id_for(self, row, col, rows, cols, stim_type):
        if stim_type == 'letter':
            return rows*cols + 2*row*cols + col
        elif stim_type == 'square':
            return rows*cols + row*cols + col
        else:
            raise Exception("An unknow stimulus type was requested!")
    def _generate_speller_stims(self, base, p_rows, p_cols, p_sq_size, p_sq_color, p_let_size, letters):
        stims = []
        stims_no = p_rows*p_cols
        
        assert(stims_no == len(letters))
        
        width = 1.0/p_cols
        height = 1.0/p_rows
        
        pos_hor = 0.0
        pos_vert = 0.0
        stim_id = 0
        for i_row in range(p_rows):
            for j_col in range(p_cols):
                stim = copy.deepcopy(base)
                stim['id'] = stim_id
                stim_id += 1
                stim['width'] = width
                stim['height'] = height
                stim['position_horizontal'] = pos_hor
                pos_hor += width
                stim['position_vertical'] = pos_vert
                
                stim_sq = stim['stimuluses'][0]
                stim_sq['id'] = stims_no + stim['id']
                stim_sq['width'] = p_sq_size
                stim_sq['height'] = p_sq_size
                stim_sq['color'] = p_sq_color
                
                stim_letter = stim_sq['stimuluses'][0]
                stim_letter['id'] = 2*stims_no + stim['id']
                stim_letter['font_size'] = p_let_size
                stim_letter['message'] = letters[stim['id']]
                stims.append(stim)
            
            pos_hor = 0.0
            pos_vert += height
        return stims
    

if __name__ == "__main__":
    generate_config()
