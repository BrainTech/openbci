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

import os.path, time
from pygame.locals import *

from arrow.draw_arrow import DrawArrow
from arrow.draw_wii_arrow import DrawWiiArrow

from screen_text.screen_text import *
from screen_text.render_textrect import render_textrect

from constants.constants_arrow import ARROW_PROPORTION, ARROW_SIZE, ARROW_COLORS_LEVELS, ARROW_LEVELS_LINES
from constants.constants_game import SIZE_OBJECT, SCREEN_SIZE, RECT_TEXT_SIZE

from obci.configs import settings
from obci.acquisition import acquisition_helper

GAME_DATA_PATH = os.path.join(settings.MAIN_DIR, 'exps/ventures/maze_game/game_data')

class MazeScreen(object):  
    def __init__(self, time_board_display, number_of_levels, session_number, session_type, session_condition):
        super(MazeScreen, self).__init__()
        pygame.init()

        self.session_type = session_type
        self.session_condition = session_condition


        self.size_object = SIZE_OBJECT

        self.arrow_proportion = ARROW_PROPORTION
        self.arrow_size = ARROW_SIZE
        self.arrow_colors_levels = ARROW_COLORS_LEVELS
        self.arrow_levels_lines = ARROW_LEVELS_LINES

        self.screen_size = SCREEN_SIZE
        self.time_board_display = time_board_display
        self.session_number = session_number
        self.number_of_levels = number_of_levels
        self.screen = pygame.display.set_mode(self.screen_size, FULLSCREEN)
        pygame.display.init()

        self._load_font()
        self._load_sound()
        self._load_image()
        self._init_arrows()
  
        self.animation_offset_x = 0
        self.animation_offset_y = 0
        self.text_rect = pygame.Rect(RECT_TEXT_SIZE)

    def _load_font(self):
        pygame.font.init()
        self.font_game = pygame.font.Font(os.path.join(GAME_DATA_PATH,'impact.ttf'), 18)
        self.font_text = pygame.font.Font(os.path.join(GAME_DATA_PATH,'impact.ttf'), 24)

    def _load_sound(self):
        self.hit_wall_sound = pygame.mixer.Sound(os.path.join(GAME_DATA_PATH,'Boom.wav'))
        self.fall_sound = pygame.mixer.Sound(os.path.join(GAME_DATA_PATH,'Fall.wav'))
        self.enter_sound = pygame.mixer.Sound(os.path.join(GAME_DATA_PATH, 'Enter.wav'))

    def _load_image(self):
        self.ball = pygame.image.load(os.path.join(GAME_DATA_PATH,'ball.png'))
        self.block = pygame.image.load(os.path.join(GAME_DATA_PATH,'block.gif'))
        self.floor_block = pygame.image.load(os.path.join(GAME_DATA_PATH,'floor.gif'))
        self.hole_block = pygame.image.load(os.path.join(GAME_DATA_PATH,'hole.gif'))

        if self.sesion_condition == 'motor':
            self.start_block = pygame.image.load(os.path.join(GAME_DATA_PATH,'start_path.gif'))
        else:
            self.start_block = pygame.image.load(os.path.join(GAME_DATA_PATH,'start.gif'))

        self.finish_block = pygame.image.load(os.path.join(GAME_DATA_PATH,'finish.gif'))
        self.black_screen = pygame.image.load(os.path.join(GAME_DATA_PATH,'blank.gif'))
        self.floor_path_block = pygame.image.load(os.path.join(GAME_DATA_PATH,'floor_path.gif'))
        self.floor_active_path_block = pygame.image.load(os.path.join(GAME_DATA_PATH,'floor_path_2.gif'))

    def _init_arrows(self):
        if self.session_condition == 'cognitive':
            self.arrow_right = DrawArrow(self.screen, 'right', self.arrow_colors_levels, 
                                         self.arrow_proportion, self.arrow_size, self.arrow_levels_lines)
            self.arrow_left = DrawArrow(self.screen, 'left', self.arrow_colors_levels, 
                                        self.arrow_proportion, self.arrow_size, self.arrow_levels_lines)
            self.arrow_up = DrawArrow(self.screen, 'up', self.arrow_colors_levels, 
                                      self.arrow_proportion, self.arrow_size, self.arrow_levels_lines)
            self.arrow_down = DrawArrow(self.screen, 'down', self.arrow_colors_levels, 
                                        self.arrow_proportion, self.arrow_size, self.arrow_levels_lines)
        
        elif self.session_condition in ['motor', 'motor_cognitive']:
            self.arrow_right = DrawWiiArrow(self.screen, 'right', self.arrow_colors_levels, 
                                            self.arrow_proportion, self.arrow_size, self.arrow_levels_lines)
            self.arrow_left = DrawWiiArrow(self.screen, 'left', self.arrow_colors_levels, 
                                           self.arrow_proportion, self.arrow_size, self.arrow_levels_lines)
            self.arrow_up = DrawWiiArrow(self.screen, 'up', self.arrow_colors_levels, 
                                         self.arrow_proportion, self.arrow_size, self.arrow_levels_lines)
            self.arrow_down = DrawWiiArrow(self.screen, 'down', self.arrow_colors_levels, 
                                           self.arrow_proportion, self.arrow_size, self.arrow_levels_lines)

    def get_arrow(self, type_):
        if type_ == 'right':
            return self.arrow_right

        elif type_ == 'left':
            return self.arrow_left

        elif type_ == 'up':
            return self.arrow_up

        elif type_ == 'down':
            return self.arrow_down

    def load_wii_level_arrow_proportion(self, direction, proportion):
        self.get_arrow(direction).set_arrow_proportion(proportion)

    def _calc_grid_offsets(self, level):
        self.x_offset = (self.screen_size[0] -(((len(level))*self.size_object)))/2
        self.y_offset = (self.screen_size[1] - (((len(level[0]))*self.size_object)))/2

    def _get_position(self, xm, ym):
        x_position = (xm*self.size_object) + self.x_offset
        y_position = (ym*self.size_object) + self.y_offset
        return (x_position, y_position)

    def draw_game(self, level_array, ball_position_x, ball_position_y, current_level, 
                  level_time, sesion_time, path, active_path):
        self._draw_level(level_array, path)
        self._draw_active_path(active_path)
        self._draw_ball(ball_position_x, ball_position_y)
        self._draw_level_info(current_level, level_time, session_time)
        self._display()

    def draw_game_with_arrow(self, arrow_type, level_array, ball_position_x, ball_position_y, 
                             current_level, level_time, sesion_time, path, active_path):
        self._draw_level(level_array, path)
        self._draw_active_path(active_path)
        self._draw_ball(ball_position_x, ball_position_y)
        self._draw_level_info(current_level, level_time, session_time)
        self._draw_arrow(arrow_type, ball_position_x, ball_position_y)
        self._display()
        
    def draw_game_with_arrow_update(self, arrow_type, arrow_level, level_array, ball_position_x, 
                                    ball_position_y, current_level, level_time, sesion_time, path, active_path):
        self._draw_level(level_array, path)
        self._draw_active_path(active_path)
        self._draw_ball(ball_position_x, ball_position_y)
        self._draw_level_info(current_level, level_time, session_time)
        self.get_arrow(arrow_type).draw_level(arrow_level)
        self._display()

    def draw_game_with_wii_arrow(self, arrow_type, arrow_level, arrow_area_param, level_array, ball_position_x, 
                                 ball_position_y, current_level, level_time, sesion_time, path, active_path):
        self._draw_level(level_array, path)
        self._draw_active_path(active_path)
        self._draw_ball(ball_position_x, ball_position_y)
        self._draw_level_info(current_level, level_time, session_time)
        self._draw_arrow(arrow_type, ball_position_x, ball_position_y)
        self.get_arrow(arrow_type).draw_level(arrow_level, arrow_area_param)
        self._display()

    def draw_game_with_wii_arrow_update(self, arrow_type, arrow_level, arrow_area_param, level_array, ball_position_x, 
                                        ball_position_y, current_level, level_time, sesion_time, path, active_path):
        self._draw_level(level_array, path)
        self._draw_active_path(active_path)
        self._draw_ball(ball_position_x, ball_position_y)
        self._draw_level_info(current_level, level_time, session_time)
        self.get_arrow(arrow_type).draw_level(arrow_level, arrow_area_param)
        self._display()

    def _draw_level(self, level, path):
        self.screen.blit(self.black_screen, (0,0))
        self._calc_grid_offsets(level)
        for ym in range(len(level)):
            for xm in range(len(level[0])):
                if level[ym][xm] == 0:
                    self.screen.blit(self.floor_block, self._get_position(xm, ym))

                elif level[ym][xm] == 1:
                    self.screen.blit(self.block, self._get_position(xm, ym))

                elif level[ym][xm] == 2:
                    self.screen.blit(self.hole_block, self._get_position(xm, ym))

                elif level[ym][xm] == 3:
                    self.screen.blit(self.start_block, self._get_position(xm, ym))

                elif level[ym][xm] == 4:
                    self.screen.blit(self.finish_block, self._get_position(xm, ym))
        if self.sesion_condition == 'motor':
            for ym, xm in path:
                self.screen.blit(self.floor_path_block, self._get_position(xm, ym))
            else:
                pass

    def _draw_active_path(self, active_path):
        if self.sesion_condition == 'motor':
            for ym, xm in active_path:
                self.screen.blit(self.floor_active_path_block, self._get_position(xm, ym))
        else:
            pass


    def _draw_ball(self, ball_x, ball_y):
        x_position, y_position = self._get_position(ball_x, ball_y)
        self.screen.blit(self.ball, (x_position+self._get_animation_offset_x(), 
                                     y_position+self._get_animation_offset_y()))

    def _draw_level_info(self, current_level, level_time, session_time):

        level_text = self.font_game.render('{}: {}/{}'.format('POZIOM', current_level, self.number_of_levels), 
                                            1, 
                                            (250, 250, 250))
        self.screen.blit(level_text, (0, 20))
        #level_text = self.font_game.render('{}: {}'.format('POZIOM', level_time), 
        #                                    1, 
        #                                    (250, 250, 250))
        #self.screen.blit(level_text, (0, 40))
        if self.session_type == 'experiment':
            level_text = self.font_game.render('{}: {}'.format('CZAS', session_time), 
                                                1, 
                                                (250, 250, 250))
            self.screen.blit(level_text, (0, 40))

    def _draw_arrow(self, type_, ball_x, ball_y):
        if type_ == 'right':
            self._draw_arrow_right(ball_x, ball_y)

        elif type_ == 'left':
            self._draw_arrow_left(ball_x, ball_y)

        elif type_ == 'up':
            self._draw_arrow_up(ball_x, ball_y)

        elif type_ == 'down':
            self._draw_arrow_down(ball_x, ball_y)

    def _draw_arrow_right(self, ball_x, ball_y):
        x_position, y_position = self._get_position(ball_x, ball_y)
        self.arrow_right.init_position((x_position+self.size_object, y_position+int(0.5*self.size_object)))
        self.arrow_right.init_draw_arrow()

    def _draw_arrow_left(self, ball_x, ball_y):
        x_position, y_position = self._get_position(ball_x, ball_y)
        self.arrow_left.init_position((x_position, y_position+int(0.5*self.size_object)))
        self.arrow_left.init_draw_arrow()

    def _draw_arrow_up(self, ball_x, ball_y):
        x_position, y_position = self._get_position(ball_x, ball_y)
        self.arrow_up.init_position((x_position+int(self.size_object*0.5), y_position))
        self.arrow_up.init_draw_arrow()

    def _draw_arrow_down(self, ball_x, ball_y):
        x_position, y_position = self._get_position(ball_x, ball_y)
        self.arrow_down.init_position((x_position+int(self.size_object*0.5), y_position+self.size_object))
        self.arrow_down.init_draw_arrow()

    def play_sound(self, action):
        if action == 'win':
            self.enter_sound.play()

        elif action == 'level_down':
            self.fall_sound.play()

        elif action == 'hit_wall':
            self.hit_wall_sound.play()

        elif action == 'fall':
            self.fall_sound.play()

    def _display_screen_helper(self, image, text='', color=(250, 250, 250)):
        self.screen.blit(self.black_screen, (0, 0))
        rendered_text = render_textrect(text, self.font_text, self.text_rect, color, (0, 0, 0), 1)
        text = self.font_text.render(text ,1, color)
        self.screen.blit(rendered_text, self.text_rect.topleft)

    def display_screen(self, action):
        if action == 'win':
            self._display_screen_helper(text=get_win_level_text(self.session_type, self.session_condition), image=self.black_screen)
            self._display()
            time.sleep(self.time_board_display+1)

        elif action == 'start':
            self._display_screen_helper(text=get_start_session_text(self.session_number, self.session_type, self.session_condition), image=self.black_screen)
            self._display()

        elif action == 'repeat_level_1':
            self._display_screen_helper(text=get_repeat_level_text(1, self.session_type, self.session_condition), image=self.black_screen)
            self._display()
            time.sleep(self.time_board_display)

        elif action == 'repeat_level_2':
            self._display_screen_helper(text=get_repeat_level_text(2, self.session_type, self.session_condition), image=self.black_screen)
            self._display()
            time.sleep(self.time_board_display)

        elif action == 'level_down':
            self._display_screen_helper(text=get_repeat_level_text(3, self.session_type, self.session_condition), image=self.black_screen)
            self._display()
            time.sleep(self.time_board_display+2)

        elif action == 'level_timeout':
            self._display_screen_helper(text=get_timeout_level(self.session_type, self.session_condition), image=self.black_screen)
            self._display()
            time.sleep(self.time_board_display)

        elif action == 'pause':
            self._display_screen_helper(text=get_pause_text(self.session_type, self.session_condition), image=self.black_screen)
            self._display()

        elif action == 'finish':
            self._display_screen_helper(text=get_finish_session_text(self.session_number, self.session_type, self.session_condition), image=self.black_screen)
            self._display()
            time.sleep(self.time_board_display)

        elif action == 'instruction1':
            self._display_screen_helper(text=get_instruction_1(self.session_type, self.session_condition), image=self.black_screen)
            self._display()

        elif action == 'instruction2':
            self._display_screen_helper(text=get_instruction_2(self.session_type, self.session_condition), image=self.black_screen)
            self._display()

        elif action == 'exit':
            self._display_screen_helper(text=get_exit_text(self.session_type, self.session_condition), image=self.black_screen)
            self._display()

    def _display(self):
        pygame.display.flip()

    def _get_animation_offset_x(self):
        return self.animation_offset_x

    def set_animation_offset_x(self, value):
        self.animation_offset_x = value

    def update_animation_offset_x(self, value):
        self.animation_offset_x += value

    def _get_animation_offset_y(self):
        return self.animation_offset_y

    def set_animation_offset_y(self, value):
        self.animation_offset_y = value

    def update_animation_offset_y(self, value):
        self.animation_offset_y += value


