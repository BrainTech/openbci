#!/usr/bin/env python
# -*- coding: utf-8 -*-
from KontrolerKlik import KontrolerKlik
import time

def biofeedback_calibration_run(user_name, target_count):
    print "running...."
    k = KontrolerKlik()
    k.run()
    config = {'czasy_1':k.czasy, 'wspolrzedne_1':k.wspolrzedne}
    return config
