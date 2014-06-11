#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import xwiimote
import sys
import time
import select


class WiiBalanceBoard(object):
    def __init__(self):
        if len(sys.argv) == 2:
            device = sys.argv[1]
            self.iface = xwiimote.iface(device)
        else:
            device = self._wait_for_balanceboard()

        self.iface = xwiimote.iface(device)
        print self.iface 
        self.iface.open(xwiimote.IFACE_BALANCE_BOARD)
        print "opened"

    def _wait_for_balanceboard(self):
        print "Waiting for balanceboard to connect.."
        monitor = xwiimote.monitor(True, False)
        while True:
            monitor.get_fd(True) # blocks
            device = monitor.poll()

            if device == None:
                continue
            elif self._device_is_balanceboard(device):
                print "Found balanceboard:", device 
                return device
            else:
                print "Found non-balanceboard device:", connected 
                print "Waiting.." 

    def _device_is_balanceboard(self,device):
        time.sleep(2) # if we check the devtype to early it is reported as 'unknown'
        iface = xwiimote.iface(device)
        return iface.get_devtype() == 'balanceboard'

    def measurements(self):
        p = select.epoll.fromfd(self.iface.get_fd())
        while True:
            p.poll() # blocks
            event = xwiimote.event()
            self.iface.dispatch(event)
            tl = event.get_abs(2)[0]
            tr = event.get_abs(0)[0]
            br = event.get_abs(3)[0]
            bl = event.get_abs(1)[0]
            yield (time.time(), tl, tr, br, bl)