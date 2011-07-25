#!/usr/bin/env python

import pstats
import sys


def process(p_file):
    try:
        p = pstats.Stats(p_file)
    except IOError:
        print "File  ", p_file, " not found!!!"
        return -1
    
    positions = 20
    print "Top ", positions, ": cumulative time"
    p.sort_stats('cumulative').print_stats(positions)

    print ""
    print "Top ", positions, ": time spent executing function"
    p.sort_stats('time').print_stats(positions)

    print ""

    return 0


if __name__=="__main__":
    if len(sys.argv) < 2:
        print "usage: ", sys.argv[0], "[cProfile_output_file]"
        sys.exit(1)

    stats_file = sys.argv[1]
    res = process(stats_file)
    sys.exit(res)
