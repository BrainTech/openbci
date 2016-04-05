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
#      Mateusz Kruszynski <mateusz.kruszynski@gmail.com>
#

STR = ''
def to_string(p_object):
    """Convert p_object to string. Convert strings to strings, 
    floats to string with accurate precision etc."""
    try:
        p_object + STR
        # It is a string
        return p_object
    except:
        pass

    if isinstance(p_object, float):
        return repr(p_object) #Prevail precision
    else:
        return str(p_object)
