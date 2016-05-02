#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ControllerClick import ControllerClick
from Tkinter import *
import time

def biofeedback_calibration_run(target_count, pause):
    print "running...."
    root = Tk()
    my_gui = ControllerClick(root, number = target_count, pause = pause)
    my_gui.create_oval()
    root.mainloop()
    return my_gui.get_config()

if __name__ == '__main__':
    target_count = 3
    pause = 2 
    config = biofeedback_calibration_run(target_count, pause)
    print config