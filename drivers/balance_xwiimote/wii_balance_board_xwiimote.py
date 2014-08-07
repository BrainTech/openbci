#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import xwiimote
import sys
import time
import select
import time


class WiiBalanceBoard(object):
    def __init__(self):
        device = self._wait_for_balanceboard()
        if device is None:
            raise Exception("Found non-WiiBalanceBoard device")
        self.iface = xwiimote.iface(device)
        self.iface.open(xwiimote.IFACE_BALANCE_BOARD)
        self.init_pool = False

    def _wait_for_balanceboard(self):
        print "Waiting for balanceboard to connect.."
        monitor = xwiimote.monitor(True, False)
        t = time.time()
        print "Start searching for WiiBalanceBoard device..."
        while time.time()-t < 30:
            monitor.get_fd(False)
            device = monitor.poll()
            if device != None and self._device_is_balanceboard(device):
                return device
            else:
                print "Found non-WiiBalanceBoard device"
                print "Waiting.."
        return device

    def _device_is_balanceboard(self,device):
        time.sleep(2)
        iface = xwiimote.iface(device)
        return iface.get_devtype() == 'balanceboard'

    def _init_pool(self):
        self.init_pool = True
        self.p = select.epoll.fromfd(self.iface.get_fd())

    def measurment(self):
        if not init_pool:
            self._init_pool()
        self.p.poll()
        event = xwiimote.event()
        t = time.time()
        self.iface.dispatch(event)
        tl = event.get_abs(2)[0]
        tr = event.get_abs(0)[0]
        br = event.get_abs(3)[0]
        bl = event.get_abs(1)[0]
        return [tl, tr, br, bl], t