#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import time

print "to ja"
if __name__ == '__main__':

	print "Heello"
	if len(sys.argv) > 1:
		msg = sys.argv[1]
	else:
		msg = "Tralala"

	cnt = 1

	for i in range(5):
		print "Message {0}: {1}".format(cnt, msg)
		time.sleep(0.3)
		cnt += 1