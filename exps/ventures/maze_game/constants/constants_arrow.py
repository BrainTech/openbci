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

from pygame.locals import *

ARROW_SIZE = [0, 120]
ARROW_PROPORTION = [37.5, 47.5+37.5, 47.5+37.5+15.0]
ARROW_SIZE = 120
ARROW_MAX_LEVEL = 142
ARROW_LEVELS_LINES = False

ARROW_KEY = {'left' : K_LEFT,
             'right' : K_RIGHT,
             'down' : K_DOWN, 
             'up' : K_UP}

ARROW_TIME = 3

ARROW_SPEED_UP = float(ARROW_SIZE)/ARROW_TIME

ARROW_SPEED_DOWN = float(ARROW_SIZE)/ARROW_TIME

ARROW_COLORS_LEVELS  = ['green', 'green', 'green']
