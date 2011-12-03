#!/usr/bin/python
# -*- coding: utf-8 -*-

from launcher.subprocess_monitor import SubprocessManager
import time

process = SubprocessManager().new_local_process('infinite_print.py', ['asdfjkl;'],
												must_register=False)


for i in range(10):
	print process.tail_stdout(lines=3)
	time.sleep(1)

process.kill()
time.sleep(1)