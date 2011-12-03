#!/usr/bin/python
# -*- coding: utf-8 -*-

from launcher.subprocess_monitor import SubprocessManager
import time

process, details = SubprocessManager().new_local_process('infinite_print.py', ['asdfjkl;'])
print process
if process is None:
	print details
else:
	for i in range(10):
		out = process.tail_stdout(lines=12)
		while out:
			print "LINE: ", out.pop()[:-1]
		time.sleep(1)
	print "STATUS: ", process.status
process.kill()
