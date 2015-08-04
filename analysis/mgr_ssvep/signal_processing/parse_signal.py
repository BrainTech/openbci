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

from obci.analysis.obci_signal_processing import smart_tags_manager as SMGR
from obci.analysis.obci_signal_processing.tags import smart_tag_definition as DEF


def to_volts(signal, channels_gains):
    gains_matrix = np.zeros((signal.shape[0], signal.shape[0]))
    for i, gain in enumerate(channels_gains):
        gains_matrix[i, i] = gain

    return np.dot(gains_matrix.T, signal)

def signal_segmentation(mgr, tag_duration, offset, tag_name):
    
    tag_def = DEF.SmartTagDurationDefinition(start_tag_name=tag_name,
                                             start_offset=offset, 
                                             end_offset=offset, 
                                             duration=tag_duration)

    smgr = SMGR.SmartTagsManager(tag_def, 'd', 'd', 'd', mgr)
    smart_tag = smgr.get_smart_tags()

    if offset != 0:
        _tag_def = DEF.SmartTagDurationDefinition(start_tag_name=tag_name,
                                                  start_offset=0, 
                                                  end_offset=0, 
                                                  duration=tag_duration)

        _smgr = SMGR.SmartTagsManager(_tag_def, 'd', 'd', 'd', mgr)
        _smart_tag = _smgr.get_smart_tags()

        for s_tag, s_tag2 in zip(smart_tag, _smart_tag):
            s_tag.set_tags(s_tag2.get_tags())

    return smart_tag
    




