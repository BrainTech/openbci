#!/usr/bin/python
# -*- coding: utf-8 -*-


from __future__ import print_function
import sys
from subprocess import PIPE, Popen
from threading  import Thread
import time

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue):
    for line in iter(out.readline, ''):
        queue.put(line)
    out.close()

p = Popen(['python', 'infinite_print.py', 'asdfjkl;'], stdout=PIPE, bufsize=1, close_fds=ON_POSIX)
q = Queue()
t = Thread(target=enqueue_output, args=(p.stdout, q))
t.daemon = True # thread dies with the program
t.start()

# ... do other things here

for i in range(10):
    # read line without blocking
    try:  line = q.get_nowait() # or q.get(timeout=.1)
    except Empty:
        print('no output yet')
        time.sleep(0.5)
    else: # got line
        print(line, end='')