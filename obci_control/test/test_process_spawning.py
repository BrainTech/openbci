#!/usr/bin/python
# -*- coding: utf-8 -*-

from launcher.subprocess_monitor import SubprocessMonitor, RETURNCODE
import time

process, details = SubprocessMonitor(None, '12345').new_local_process('infinite_print.py', ['asdfjkl;'],
monitoring_optflags=RETURNCODE)
print process
if process is None:
	print details
else:
	for i in range(10):
		out = process.tail_stdout(lines=12)
		while out:
			print "LINE: ", out.pop()[:-1]
		time.sleep(1)
	print "STATUS: ", process.status()
process.popen_obj.kill()

time.sleep(1.5)

process.stop_monitoring()
print "AFTER KILL: ", process.status()