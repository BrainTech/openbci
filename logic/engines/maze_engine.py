#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

import time
from obci.logic import logic_helper
from obci.gui.ugm import ugm_helper
from obci.utils import context as ctx

FWD_T = u'Wciśnij prosto'
LEFT_T = u'Wciśnij lewo'
RIGHT_T = u'Wciśnij prawo'
CONGRATULATIONS = 'Gratulacje!'
#'move' - which move is available from decision
#'dir' - direction of user`new position arrow
#'x' - user`s new x position
#'y' - user`s new y position
#'robot' - robot command
#'tooltip' - tooltip for new user`s position

START_LINE = [
    {'move':'UP', 'dir':'UP', 'x':2, 'y':3, 'robot':'forward', 'tooltip':FWD_T},
    {'move':'UP', 'dir':'UP', 'x':2, 'y':2, 'robot':'forward', 'tooltip':u'Wciśnij prawo lub w lewo'},
    {'move':'NO_MOVE'}
    ]
LEFT_LINE = [
    {},
    {},
    {'move':'LEFT', 'dir':'LEFT', 'x':1, 'y':2, 'robot':'left_forward', 'tooltip':LEFT_T},
    {'move':'LEFT', 'dir':'DOWN', 'x':1, 'y':3, 'robot':'left_forward', 'tooltip':RIGHT_T},
    {'move':'RIGHT', 'dir':'LEFT', 'x':0, 'y':3, 'robot':'right_forward', 'tooltip':RIGHT_T},
    {'move':'RIGHT', 'dir':'UP', 'x':0, 'y':2, 'robot':'right_forward', 'tooltip':FWD_T},
    {'move':'UP', 'dir':'UP', 'x':0, 'y':1, 'robot':'forward', 'tooltip':FWD_T},
    {'move':'UP', 'dir':'UP', 'x':0, 'y':0, 'robot':'forward', 'tooltip':RIGHT_T},
    {'move':'RIGHT', 'dir':'RIGHT', 'x':1, 'y':0, 'robot':'right_forward', 'tooltip':RIGHT_T},
    {'move':'RIGHT', 'dir':'DOWN', 'x':1, 'y':1, 'robot':'right_forward', 'tooltip':LEFT_T},
    {'move':'LEFT', 'dir':'RIGHT', 'x':2, 'y':1, 'robot':'left_forward', 'tooltip':LEFT_T},
    {'move':'LEFT', 'dir':'UP', 'x':2, 'y':0, 'robot':'forward', 'tooltip':CONGRATULATIONS},
    {'move':'NO_MOVE'}
    ]
RIGHT_LINE = [
    {},
    {},
    {'move':'RIGHT', 'dir':'RIGHT', 'x':3, 'y':2, 'robot':'right_forward', 'tooltip':RIGHT_T},
    {'move':'RIGHT', 'dir':'DOWN', 'x':3, 'y':3, 'robot':'right_forward', 'tooltip':LEFT_T},
    {'move':'LEFT', 'dir':'RIGHT', 'x':4, 'y':3, 'robot':'left_forward', 'tooltip':LEFT_T},
    {'move':'LEFT', 'dir':'UP', 'x':4, 'y':2, 'robot':'left_forward', 'tooltip':FWD_T},
    {'move':'UP', 'dir':'UP', 'x':4, 'y':1, 'robot':'forward', 'tooltip':FWD_T},
    {'move':'UP', 'dir':'UP', 'x':4, 'y':0, 'robot':'forward', 'tooltip':LEFT_T},
    {'move':'LEFT', 'dir':'LEFT', 'x':3, 'y':0, 'robot':'left_forward', 'tooltip':LEFT_T},
    {'move':'LEFT', 'dir':'DOWN', 'x':3, 'y':1, 'robot':'left_forward', 'tooltip':RIGHT_T},
    {'move':'RIGHT', 'dir':'LEFT', 'x':2, 'y':1, 'robot':'right_forward', 'tooltip':RIGHT_T},
    {'move':'RIGHT', 'dir':'UP', 'x':2, 'y':0, 'robot':'forward', 'tooltip':CONGRATULATIONS},
    {'move':'NO_MOVE'}
    ]

class MazeEngine(object):
    def __init__(self, configs, context=ctx.get_dummy_context('MazeEngine')):
        self.logger = context['logger']
        self._curr = 0#int(configs['initial_field'])
        self._line = START_LINE
        
    def maze_move(self, direction):
        if self._curr == 2:
            if direction == 'LEFT':
                self._line = LEFT_LINE
            elif direction == 'RIGHT':
                self._line = RIGHT_LINE
            else:
                pass #bad move
        info = self._line[self._curr]
        if info['move'] == direction:
            #make move
            ugm_helper.send_config(self.conn, 
                                   str([{'id':'1986', 
                                         'maze_user_color':'#00FFFF',
                                         'maze_user_direction': info['dir'],
                                         'maze_user_x':info['x'], 
                                         'maze_user_y':info['y']}
                                        ]), 1)
            #send to robot
            ugm_helper.send_status(self.conn, '...')
            self.robot(info['robot'])
            ugm_helper.send_config_for(self.conn, '1986', 'maze_user_color', '#222777')
            ugm_helper.send_status(self.conn, info['tooltip'])
            if len(self._line) > 4 and self._curr == len(self._line) - 2:
                self._maze_success = True
            self._curr = self._curr + 1
        else:
            ugm_helper.send_config_for(self.conn, '1986', 'maze_user_color', '#FF0000')
            time.sleep(0.5)
            ugm_helper.send_config_for(self.conn, '1986', 'maze_user_color', '#222777')
        
