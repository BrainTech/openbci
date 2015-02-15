# -*- coding: utf-8 -*-
#!/usr/bin/env python
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#     Anna Chabuda <anna.chabuda@gmail.com>
#

import pygame
pygame.mixer.init()

import sys, time
from pygame.locals import *

from maze_level import MazeLevel
from maze_screen import MazeScreen 
from timers.session_watcher import SessionWatcher
from timers.level_watcher import LevelWatcher 

from constants.constants_arrow import ARROW_KEY, ARROW_SPEED_UP, ARROW_SPEED_DOWN, ARROW_SIZE
from constants.constants_game import FRAME_RATE, GAME_KEYS
 
class MazeLogic(object):

    def __init__(self, start_level, session_number, session_duration, time_board_display,
                 time_left_out, tagger, session_type, session_condition):
        super(MazeLogic, self).__init__()
        self.start_level = start_level
        self.session_timer = SessionWatcher(session_duration, time_left_out)
        self.level = MazeLevel(session_type)
        self.number_of_levels = self.level.get_number_of_levels()
        self.screen = MazeScreen(time_board_display, self.number_of_levels, session_number, session_type, session_condition)
        self.status = True
        self.pause_status = False
        self.tagger = tagger
        self.session_number = session_number

        if session_condition in ['motor', 'key_motor']:
            self.path_check = True
        else:
            self.path_check = False

    def send_tag(self, timestamp, tag_name, tage_value=''):
        self.tagger.set_tag(timestamp, str(tag_name), str(tage_value))

    # def set_first_timestamp_to_tagger(self, timestamp):
    #     self.tagger.set_first_timestamp(timestamp)

    def save_tags(self):
        self.tagger.finish()

    def level_start(self):
        self.send_tag(time.time(), 'level_start', self.get_current_level())
        self.level_watcher = LevelWatcher(self.level.get_timeout_level())
        self.level_watcher.run()

    def level_finish(self):
        self.send_tag(time.time(), 'level_finish', self.get_current_level())

    def report_level_fail(self):
        self.level_watcher.report_level_fail()

    def get_level_fail(self):
        return self.level_watcher.get_level_fail()

    def can_level_repeat(self):
        return self.level_watcher.can_level_repeat()

    def get_level_status(self):
        return self.level_watcher.get_timer_status()

    def get_level_array(self):
        return self.level.get_level_array()

    def get_path_left(self):
        return self.level.get_path_left()

    def get_all_path(self):
        return self.level.get_all_path()

    def get_active_path(self):
        return self.level.get_active_path()

    def _clear_arrows(self):
        self.screen.arrow_right.set_level(0)
        self.screen.arrow_left.set_level(0)
        self.screen.arrow_down.set_level(0)
        self.screen.arrow_up.set_level(0)

    def load_level(self):
        self.level.load_level(self.get_current_level())
        self._clear_arrows()

    def get_current_level(self):
        return self.current_level

    def update_current_level(self):
        self.current_level+=1

    def set_current_level(self, level):
        if level:
            self.current_level=level

    def get_ball_position_x(self):
        return self.level.get_ball_x()

    def get_ball_position_y(self):
        return self.level.get_ball_y()

    def set_ball_position(self, x, y):
        self.level.set_ball_x(x)
        self.level.set_ball_y(y)

    def session_start(self):
        self.session_timer.run()
        # self.set_first_timestamp_to_tagger(self.session_timer.get_time_start())
        self.send_tag(self.session_timer.get_time_start(),'session_start', self.session_number)

    def session_finish(self):
        self.session_timer.stop()
        self.send_tag(self.session_timer.get_time_stop(), 'session_finish', self.session_number)

    def get_session_status(self):
        return self.session_timer.get_timer_status()

    def get_session_length(self):
        return self.session_timer.get_time_length()

    def update_session_status(self):
        self.status = self.get_session_status()

    def get_level_time(self):
        return self.level_watcher.get_timer_time()

    def get_session_time(self):
        return self.session_timer.get_timer_time()

    def draw_game(self):
        self.screen.draw_game(self.get_level_array(),
                             self.get_ball_position_x(),
                             self.get_ball_position_y(),
                             self.get_current_level(),
                             self.get_level_time(),
                             self.get_session_time(),
                             self.get_all_path(),
                             self.get_active_path())

    def draw_game_with_arrow(self, arrow_type):
        self.screen.draw_game_with_arrow(arrow_type,
                                         self.get_level_array(),
                                         self.get_ball_position_x(),
                                         self.get_ball_position_y(),
                                         self.get_current_level(),
                                         self.get_level_time(),
                                         self.get_session_time(),
                                         self.get_all_path(),
                                         self.get_active_path())        

    def draw_game_with_arrow_update(self, arrow_type, arrow_level):
        self.screen.draw_game_with_arrow_update(arrow_type,
                                               arrow_level,
                                               self.get_level_array(),
                                               self.get_ball_position_x(),
                                               self.get_ball_position_y(),
                                               self.get_current_level(),
                                               self.get_level_time(),
                                               self.get_session_time(),
                                               self.get_all_path(),
                                               self.get_active_path())
                                                                    
    def update_screen(self):
        self.draw_game()
        for event in pygame.event.get():                    
            if event.type == QUIT:
                self.exit_game()
            elif event.type == KEYDOWN:           
                if event.key == K_ESCAPE:
                    self.exit_game()
                elif event.key in GAME_KEYS.keys():
                    self.draw_game_with_arrow(GAME_KEYS[event.key])
                    done = self.arrow_fill(GAME_KEYS[event.key])
                    if done:
                        self.send_tag(time.time(), 'move', GAME_KEYS[event.key])
                        self.move(GAME_KEYS[event.key])

                elif event.key == K_p:
                    self.make_pause()

    def arrow_fill(self, type_):
        time_start = time.time()

        arrow = self.screen.get_arrow(type_)
        key = ARROW_KEY[type_]

        level = arrow.get_level()
        if sum(pygame.key.get_pressed()) and pygame.key.name(pygame.key.get_pressed().index(1))==type_:
            while level <= ARROW_SIZE:
                self.draw_game_with_arrow_update(type_,level)
                for event in pygame.event.get():
                    if event.type == KEYUP:
                        arrow.set_level(level)
                        self.arrow_wane(type_)
                        return False
                level += ARROW_SPEED_UP*1.0/FRAME_RATE
                time.sleep(1.0/FRAME_RATE)

            arrow.set_level(0)
            return True
        else:
            arrow.set_level(0)
            return False

    def arrow_wane(self, type_):
        time_start = time.time()
        
        arrow = self.screen.get_arrow(type_)
        key = ARROW_KEY[type_]

        level = arrow.get_level()
        while level > 0:
            self.draw_game_with_arrow_update(type_, level)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    pygame.event.post(event)
                    if event.key == key:
                        arrow.set_level(level)
                    else:
                        arrow.set_level(0)
                    return
            level -= ARROW_SPEED_DOWN*1.0/FRAME_RATE
            time.sleep(1.0/FRAME_RATE)
        arrow.set_level(0)

    def move(self, type_):
        if type_=='left':
            self._move(x_update=-1, x_animation_offset_update=-float(self.screen.size_object)/4)

        elif type_=='right':
            self._move(x_update=1, x_animation_offset_update=float(self.screen.size_object)/4)

        elif type_=='down':
            self._move(y_update=1, y_animation_offset_update=float(self.screen.size_object)/4)

        elif type_=='up':
            self._move(y_update=-1, y_animation_offset_update=-float(self.screen.size_object)/4)

        if self.path_check:
            if self.get_path_left():
                pass
            else:
                self.repeat_level()              

    def _move(self, x_update=0, y_update=0, y_animation_offset_update=0, x_animation_offset_update=0, number=0):
        self.screen.set_animation_offset_x(0)
        self.screen.set_animation_offset_y(0)
        x_position, y_position = self.get_ball_position_x(), self.get_ball_position_y()
        x_new, y_new = x_position+x_update, y_position+y_update
        if self.get_level_array()[y_new][x_new] == 2:
            self.set_ball_position(x_new, y_new)
            self.draw_game()
            self.repeat_level()

        elif self.get_level_array()[y_new][x_new] == 1: 
            self.draw_game()
            self.hit_wall()
            if (not number) and self.path_check:
                self.repeat_level()

        elif self.get_level_array()[y_new][x_new] in [0, 3]:
            for i in range(4):
                self.screen.update_animation_offset_y(y_animation_offset_update)
                self.screen.update_animation_offset_x(x_animation_offset_update)
                self.draw_game()
                time.sleep(0.025)
            self.set_ball_position(x_new, y_new)
            self._move(x_update, y_update, y_animation_offset_update, x_animation_offset_update, number=number+1)

        elif self.get_level_array()[y_new][x_new] == 4:
            self.set_ball_position(x_new, y_new)
            self.draw_game()
            self.win_level()

    def make_pause(self):
        self.send_tag(time.time(), 'pause', 'start')
        self.session_timer.make_pause()
        self.level_watcher.make_pause()
        self.pause_status=True
        self.screen.display_screen('pause')
        while self.pause_status:
            for event in pygame.event.get():                    
                if event.type == QUIT:
                    self.finish_game()
                elif event.type == KEYDOWN:            
                    if event.key == K_ESCAPE:
                        self.finish_game()
                    if event.key == K_p:
                        self.pause_status = False

        self.session_timer.finish_pause()
        self.level_watcher.finish_pause()
        self.send_tag(time.time(), 'pause', 'stop')
        self.update_session_status()
        if self.status:
            self.load_level()

    def repeat_level(self):
        self.send_tag(time.time(), 'repeat_level', self.get_level_fail())
        self.report_level_fail()
        self.screen.play_sound('fall')
        time.sleep(1.0)
        self.update_session_status()
        if self.can_level_repeat():
            if self.get_level_fail() == 1:
                self.screen.display_screen('repeat_level_1')
            elif self.get_level_fail() == 2:
                self.screen.display_screen('repeat_level_2')
        else:
            self.level_finish()
            self.screen.display_screen('level_down')
            self.set_current_level(self.get_current_level()-1)

        if self.status:
            if not self.can_level_repeat():
                self.level_start()
            self.load_level()

    def level_timeout(self):
        self.send_tag(time.time(), 'level_timeout')
        self.level_finish()
        self.update_session_status() 
        self.set_current_level(self.get_current_level()-1)
        self.screen.display_screen('level_timeout')
        if self.status:
            self.level_start()
            self.load_level() 

    def win_level(self):
        self.send_tag(time.time(), 'win')
        self.level_finish()
        self.screen.play_sound('win')
        time.sleep(1.0)
        self.update_current_level()
        self.update_session_status()
        self.screen.display_screen('win')
        if self.get_current_level()<=self.number_of_levels and self.status:
            self.load_level()
            self.level_start()

    def hit_wall(self):
        self.screen.play_sound('hit_wall')

    def finish_game(self):
        self.screen.display_screen('finish')
        self.send_tag(time.time(), 'FINISH_exit')
        self.session_finish()
        self.save_tags()
        pygame.quit()

    def exit_game(self):
        self.send_tag(time.time(), 'ESC_exit')
        self.session_timer.make_pause()
        self.level_watcher.make_pause()
        self.pause_status=True
        self.screen.display_screen('exit')
        while self.pause_status:
            for event in pygame.event.get():                    
                if event.type == KEYDOWN:            
                    if event.key == K_t:
                        self.status = False
                        return ''
                    if event.key == K_n:
                        self.pause_status = False
        self.session_timer.finish_pause()
        self.level_watcher.finish_pause()

        self.update_session_status()
        if self.status:
            self.load_level()

    def instruction(self):
        screens = ['start', 'instruction1', 'instruction2']
        screen_status = 0
        self.screen.display_screen(screens[screen_status])

        while screen_status<3:
            for event in pygame.event.get():                    
                if event.type == KEYDOWN:            
                    if event.key == K_SPACE:
                        screen_status+=1 
                        if screen_status<len(screens):
                            self.screen.display_screen(screens[screen_status])

    def main(self):    
        self.set_current_level(self.start_level)
        self.load_level()  
        self.instruction()
        self.session_start() 
        self.level_start()
        while self.get_current_level()<= self.number_of_levels and self.status:
            if not self.get_level_status():
                self.level_timeout()
            else:
                self.update_screen()
            time.sleep(1/FRAME_RATE)
        self.finish_game()
