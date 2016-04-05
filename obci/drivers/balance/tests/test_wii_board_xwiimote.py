#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import numpy as np
import obci.drivers.balance.wii_board_xwiimote as wii_board_xwiimote
from obci.analysis.balance import wii_utils

def format_measurement(x):
    return "{0:.2f}".format(x/ 100.0)

def print_bboard_measurements(tl, tr, br, bl):
    sum_mass = float(tr)+ float(tl) + float(br) + float(bl) 
    x = (((float(tr) + float(br)) - (float(tl) + float(bl)))/sum_mass)
    y = (((float(tr) + float(tl)) - (float(br) + float(bl)))/sum_mass)

    xx, yy = wii_utils.get_x_y(tl, tr, br, bl)
    assert(xx==x)
    assert(yy==y)

    print x, y
    print "{}{}{}".format("┌","─" * 21, "┐")
    print "{}{}{}{}{}".format("│"," " * 8, "{:>5}".format(sum_mass)," " * 8, "│")
    print "{}{}{}{}{}".format("├","─" * 10, "┬", "─" * 10, "┤")
    print "│{:^10}│{:^10}│".format(tl, tr)
    print "{}{}{}{}{}".format("│"," " * 10, "│", " " * 10, "│")
    print "{}{}{}{}{}".format("│"," " * 10, "│", " " * 10, "│")
    print "│{:^10}│{:^10}│".format(bl, br)
    print "{}{}{}{}{}".format("└","─" * 10, "┴", "─" * 10, "┘")
    print "{}".format('\n\n')

def main():
    wbb = wii_board_xwiimote.WiiBalanceBoard()
    t = time.time()
    fs = []
    i = 0
    try:
        while True:
            tl,tr,br,bl, m_t = wbb.measurment()
            if i:
                fs.append(1.0/(m_t-t_last))
            print 'time: {0:.2f} s'.format(m_t-t)
            print_bboard_measurements(tl, tr, br, bl)
            t_last = m_t
            i+=1

    except KeyboardInterrupt:
        print "\nestimate fs: {} +/- {} Hz".format(np.mean(fs), np.std(fs))

if __name__ == '__main__':
    main()
