#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

from openbci.data_storage import csv_manager
from openbci import settings
import os.path
f1 = os.path.join(settings.module_abs_path(), "csv_test1.csv")
mgr = csv_manager.Writer(f1)

mgr.write_row([u'źbło',u'b',u'c'])
mgr.write_row(['', ''])
mgr.write_row([1,2.1, 3])
mgr.close()

f2 = os.path.join(settings.module_abs_path(), "csv_test2.csv")
mgr1 = csv_manager.Writer(f2)

mgr2 = csv_manager.Reader(f1)
for i in mgr2:
    print(i)
    mgr1.write_row(i)

mgr1.close()
mgr2.close()
print("See csv_test.csv and csv_test2.csv files.")
