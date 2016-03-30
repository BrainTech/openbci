#!/usr/bin/env python
# -*- coding: utf-8 -*-zzz

import time
import random


class WiiBalanceBoard(object):
    def __init__(self):
        pass
    def measurment(self):
        time.sleep(1.0/80.0)
        return random.random(), random.random(), random.random(), random.random(), time.time()
