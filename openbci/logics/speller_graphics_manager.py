# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
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
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#


class SpellerGraphicsManager(object):
    """Handle graphics data format between logics and ugm.
    This mean:
    - pack data to string before sending it to ugm,
    - unpack data in ugm so that it is understandable by ugm.
    """
    DIVIDER = ' :: | '
    HEAD = ' | '
    TAIL = ' '
    def pack(self, p_graphics_elements):
        """For given collection of strings to be displayed in ugm
        return a string representing this collection. 
        The method is fired in logic, just before sendin data to ugm.
        See self.unpack method te learn how to receive data in ugm.
        """
        l_tmp_packed = SpellerGraphicsManager.DIVIDER.join(p_graphics_elements)
        l_packed = ''.join([SpellerGraphicsManager.HEAD, 
                           l_tmp_packed, 
                           SpellerGraphicsManager.TAIL])
        return l_packed
    def unpack(self, p_packed_graphics):
        """For given string p_packed_graphics return a collection of
        strings understandable by ugm. 
        The method is fired in ugm, just after receiving data from logic.
        See self.pack method te learn how to send data to ugm.
        """
        l_squares = p_packed_graphics.split('::')
        for i in range(len(l_squares)):
            l_squares[i] = l_squares[i].split('|')
            l_squares[i] = [x.strip() for x in l_squares[i]]
        return l_squares
