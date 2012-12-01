#!/usr/bin/python
# -*- coding: utf-8 -*-

#from launcher.subprocess_monitor import SubprocessMonitor, RETURNCODE
import time
import subprocess
import sys
# process, details = SubprocessMonitor(None, '12345').new_local_process('infinite_print.py', ['asdfjkl;'],
# monitoring_optflags=RETURNCODE)
# print process
# if process is None:
#     print details
# else:
#     for i in range(4):
#         out = process.tail_stdout(lines=12)
#         while out:
#             print "LINE: ", out.pop()[:-1]
#         time.sleep(1)
#     print "STATUS: ", process.status()
# process.kill()

# time.sleep(1.5)


# print "AFTER KILL: ", process.status()
f = open('/home/lis/__tmp__', 'a', 0)
f.write("HAHAHAHA\n")

sys.stdout = sys.stderr = f
proc = subprocess.Popen(['python','/host/dev/openbci/control/test/infinite_print.py'], stdout=f, stderr=f)

for i in range(10):
    #t = subprocess.Popen(['tail', '/home/lis/__tmp__'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #std, err = t.communicate()
    #print 'c', std,
    #print "...", err
    time.sleep(1)
f.close()
proc.kill()
