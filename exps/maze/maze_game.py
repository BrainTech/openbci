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

import os.path

from maze_game.maze_logic import MazeLogic
from maze_game.tags.tagger import Tagger
from maze_game.user_data.parse_user_data import ParseUserData

class MazeGame(object):
    def __init__(self, user_name, 
                 config_sesion_file_name='sesions_data.csv', config_sesion_file_path='./maze_game/user_data',
                 config_users_file_name='users_data.csv', config_users_file_path='./',
                 sesion_duration=30*60, time_board_display=5, time_left_out=30, 
                 maze_path_display=False, tag_file_path='',tag_status=True):
        super(MazeGame, self).__init__()
        self.user_name = user_name
        self.config_sesion_file = os.path.join(config_sesion_file_path, 
                                               config_sesion_file_name)
        self.config_users_file = os.path.join(config_users_file_path, 
                                              config_users_file_name)

        self.user_data_parser = ParseUserData(self.config_users_file, self.config_sesion_file)

        self.sesion_number, self.start_level= self._get_start_info(self.user_name)
        self.sesion_duration = sesion_duration
        self.time_board_display = time_board_display
        self.time_left_out = time_left_out
        self.maze_path_display = maze_path_display

        self.tagger_init(tag_file_path, self.user_name, self.sesion_number, tag_status)

    def tagger_init(self, tag_file_path, user_name, sesion_number, tag_status):
        if tag_status:
            self.tagger = Tagger(tag_file_path, user_name, sesion_number, status='ON')
        else:
            self.tagger = Tagger(tag_file_path, user_name, sesion_number, status='OFF')

    def _get_start_info(self, user_name):
        return self.user_data_parser.get_user_trening_data(user_name)

    def finish_saving(self, end_level):
        self.user_data_parser.set_sesion_data(self.user_name, self.sesion_number, end_level)

    def run(self):
        game = MazeLogic(self.start_level, self.sesion_number, self.sesion_duration, self.time_board_display, 
                       self.time_left_out, self.maze_path_display, self.tagger)
        game.main()
        self.finish_saving(game.get_current_level())

if __name__ == '__main__':
    a = MazeGame('test')
    a.run()
