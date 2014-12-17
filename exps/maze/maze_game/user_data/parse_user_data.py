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

import pandas as pd
from .. constants.constants_file_data import *

class ParseUserData(object):
    def __init__(self, file_user, file_sesion):
        super(ParseUserData, self).__init__()
        self.file_user_name = file_user
        self.file_sesion_name = file_sesion

        self.user_data = self._read_file(self.file_user_name, columns=USERS_COL)
        self.sesion_data = self._read_file(self.file_sesion_name, columns=SESION_COL)
        self._update_sesion_data()

    def _read_file(self, file_name, columns):
        data = pd.read_csv(file_name, index_col=False, usecols=columns)
        return data

    def _update_sesion_data(self):
        init_users = self.sesion_data['ID'].values
        all_user = self.user_data['ID'].values

        for user_id in all_user:
            if not user_id in init_users:
                user_data = pd.DataFrame({label:[value] for label, value in zip(SESION_COL, self._get_init_sesion_values(user_id))})
                self.sesion_data = self.sesion_data.append(user_data)
        self.sesion_data = self.sesion_data.set_index([range(0, len(self.sesion_data.values))])

    def _get_init_sesion_values(self, user_id):
        return [user_id, '', '', '', '', '', '', '', '', '', '']

    def _get_user_id(self, user_name):
        return self.user_data[self.user_data['user_name']==user_name]['ID'].values[0]

    def _update_file_sesion_data(self):
        self.sesion_data.to_csv(self.file_sesion_name, col=SESION_COL)

    def get_user_trening_data(self, user_name):
        id_user = self._get_user_id(user_name)
        sesion_data = self.sesion_data[self.sesion_data['ID']==id_user]

        sesion_data = [int(sesion_data['sesion_{}'.format(number)].values[0]) for number in range(1, 11) 
                        if sesion_data['sesion_{}'.format(number)].values[0] != '' 
                            and str(sesion_data['sesion_{}'.format(number)].values[0]) != 'nan' ]

        current_sesion = len(sesion_data)+1
        if not len(sesion_data):
            start_level = 1
        else:
            start_level = sesion_data[-1]
        return current_sesion, start_level

    def set_sesion_data(self, user_name, current_sesion, stop_level):
        id_user = self._get_user_id(user_name)
        index = self.sesion_data[self.sesion_data['ID']==id_user].index[0]
        self.sesion_data = self.sesion_data.set_value(index, 'sesion_{}'.format(current_sesion), stop_level)
        self._update_file_sesion_data()












        
