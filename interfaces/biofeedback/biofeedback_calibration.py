#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ControllerClickNew import ControllerClick
from Tkinter import *
import time

def biofeedback_calibration_run(target_count, pause, time_exp):
    print "running...."
    my_gui = ControllerClick(number = target_count, pause = pause, time_exp=time_exp)
    my_gui.mainloop()
    return my_gui.get_config()

if __name__ == '__main__':
    target_count = 3
    pause = 2 
    time_exp = 4
    config = biofeedback_calibration_run(target_count, pause, time_exp)
    print config
