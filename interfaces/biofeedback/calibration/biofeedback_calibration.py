#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
import os
from SlideShowPics import main

def biofeedback_calibration_run():
    print "running...."
    curntPaths = os.getcwd()
    if len(sys.argv) > 1:
        curntPaths = sys.argv[1:]
    main(curntPaths)

if __name__ == '__main__':
	biofeedback_calibration_run()
