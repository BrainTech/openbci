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

from Xlib import X, display, Xutil, XK
def wait(p_keys_list):
    """Block the whole keyboard!!! And wait until some key from p_keys_list
    is pressed. By now p_keys_list is a list of strings, so use single
    ascii symbols.
    There is a way out of this hell - hit 'Escape'.
    The function returns hit button`s string representation
    Eg. for p_keys_list == ['1','2','3'] the function will hand untill
    1,2 or 3 key is preseed or Escape is pressed."""
    ds = display.Display()
    screen = ds.screen()
    window = screen.root
    window.grab_keyboard(1, X.GrabModeAsync, X.GrabModeAsync, X.CurrentTime)
    while True:
        ev = ds.next_event()
        if ev.type == X.KeyPress:
            keysym = ds.keycode_to_keysym(ev._data['detail'], 0)
            keystr = XK.keysym_to_string(keysym)
            if keystr in p_keys_list:
                ds.ungrab_keyboard(X.CurrentTime)
                ds.flush()
                return keystr
            elif keysym == 65307:
                ds.ungrab_keyboard(X.CurrentTime)
                ds.flush()
                return 'Escape'

if __name__ == "__main__":
    import sys,time
    print(wait(sys.argv[1:]))
    time.sleep(10)
    
    
