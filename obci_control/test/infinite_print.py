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
		print "Message {0}: {1}".format(cnt, msg)
		time.sleep(0.3)
		print >> sys.stderr, "Err msg {0}".format(cnt)
		cnt += 1