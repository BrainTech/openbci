#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time


if __name__ == '__main__':

	print "Heello"
	print "to ja"
	if len(sys.argv) > 1:
		msg = sys.argv[1]
	else:
		msg = "Tralala"

	cnt = 1

	while True:
		print >>sys.stdout," Message {0}: {1}".format(cnt, msg)

		print >> sys.stderr, "Err msg {0}".format(cnt)
		cnt += 1
		time.sleep(0.5)