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

import numpy as np

def get_montage_matrix(all_channels, use_channels, montage_type, 
                       montage_channels, leave_channels=[]):
    montage_matrix = np.zeros((len(all_channels), 
                               len(use_channels)+len(leave_channels)))

    for i, ch_names in enumerate(use_channels):
        ch_ind = all_channels.index(ch_names)
        montage_matrix[ch_ind, i] = 1.0

    for i, ch_names in enumerate(leave_channels, 
                                 len(use_channels)):

        ch_ind = all_channels.index(ch_names)
        montage_matrix[ch_ind, i] = 1.0

    if montage_type == 'ident':
        return montage_matrix

    elif montage_type == 'ears':
        e1 = all_channels.index(montage_channels[0])
        e2 = all_channels.index(montage_channels[1])

        for use_ch_ind in range(len(use_channels)):
            montage_matrix[e1, use_ch_ind] = -0.5
            montage_matrix[e2, use_ch_ind] = -0.5

    elif montage_type == 'diff':
        d = all_channels.index(montage_channels[0])

        for use_ch_ind in range(len(use_channels)):
            montage_matrix[d, use_ch_ind] = -1.0

    return montage_matrix


def montage(signal, montage_matrix):
    return np.dot(montage_matrix.T, signal)