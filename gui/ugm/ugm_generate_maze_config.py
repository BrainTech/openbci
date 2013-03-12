#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
from obci.gui.ugm import ugm_config_manager as m
MAZE = {'id':'1986', 
        'stimulus_type':'maze',
        'width_type':'relative', 
        'width':1.0,
        'height_type':'relative',
        'height':1.0,
        'position_horizontal_type':'aligned',
        'position_horizontal':'center', 
        'position_vertical_type':'aligned',
        'position_vertical':'center',
        'color':'#ffffff',
        'maze_user_x':2,
        'maze_user_y':4,
        'maze_user_direction':'UP',
        'maze_user_color':'#222777',
        'stimuluses':[]
        }

def run(maze_parent_id=102,
        output_path='configs/speller_config_8_no_letters_tablet_maze.ugm',
        template='speller_config_8_no_letters_tablet'):
    mgr = m.UgmConfigManager(template)
    parent = mgr.get_config_for(maze_parent_id)
    parent['stimuluses'].append(MAZE)
    mgr.set_config(parent)
    mgr.update_to_file(output_path)

if __name__ == '__main__':
    run()
