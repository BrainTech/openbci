#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import time

from collections import deque
try:
    from Queue import Queue, Empty, Full
except ImportError:
    from queue import Queue, Empty, Full  # python 3.x



STDIO_QUEUE_MAX_SIZE = 8192
STDIO_TAIL_LEN = 128
DEFAULT_TAIL_RQ = 10

LINES_TO_GET = 5
IO_WAIT = 0.5


class ProcessIOHandler(object):
    """Processes data from descriptors (stdout, stderr) in separate threads.
    Access to the tail is available through attributes *out_tail* and *err_tail*.
    Communication through stdin, if given, is possible by *communicate()* method.
    Data is saved to log files if the handles were given in init.
    """
    def __init__(self, name, stdout=None, stderr=None, stdin=None,
                            out_log=None, err_log=None):
        self.name = name
        self.stdout = stdout
        self.stdin = stdin
        self.stderr = stderr

        self._output_handler_thread = None
        self._stop = False

        self._out_q, self._stdout_thread, self._out_log = \
                                self.__init_io(self.stdout, out_log)

        self.out_tail = deque(maxlen=STDIO_TAIL_LEN)
        self.err_tail = deque(maxlen=STDIO_TAIL_LEN)


        self._err_q, self._stderr_thread, self._err_log = \
                                    self.__init_io(self.stderr, err_log)

        if self.stdout or self.stderr:
            self._start_background_io_reading()

    def __init_io(self, stream, log_name):

        q, thr, log = None, None, None
        if stream is not None:
            q = Queue(maxsize=STDIO_QUEUE_MAX_SIZE)
            thr = threading.Thread(target=self._read, args=(stream, q))
            thr.daemon = True

            if log_name:
                try:
                    log = open(log_name, 'w', buffering=0)
                except IOError:
                    print "{0} : Could not open log {1}".format(self.name, log_name)
        return q, thr, log

    def communicate(self, input, response_timeout=None):
        #TODO :)
        return None

    def tail_stdout(self, lines):
        data = []
        for l in range(lines):
            try:
                data.append(self.out_tail.pop())
            except IndexError:
                break
        return list(reversed(data))

    def process_output(self, lines=None, timeout=None):
        """Check if there is data from stdout and stderr (if it is monitored).
        Update tail and save data to logs, if they were given in init.
        Timeout (s) means blocking queue reads, no timeout - non blocking.
        """
        if self.stdout:
            self._handle_stdout(lines=lines, timeout=timeout)
        if self.stderr:
            self._handle_stderr(lines=lines, timeout=timeout)

    def start_output_handler(self):
        self._output_handler_thread = threading.Thread(
                                        target=self._output_handler)
        self._output_handler_thread.deamon = True
        self._output_handler_thread.start()

    def stop_output_handler(self):
        self._stop = True
        self._output_handler_thread.join(timeout=0.1)
        if self.stdout:
            self._stdout_thread.join(timeout=0.1)
        if self.stderr:
            self._stderr_thread.join(timeout=0.1)
        return self.finished()

    def is_running(self):
        return self._stop == False and self.__io_readers_alive()

    def finished(self):
        return (not self.__io_readers_alive()) and \
                (not self._output_handler_thread.is_alive())

    def __io_readers_alive(self):
        alive = False
        if self.stdout:
            alive = self._stdout_thread.is_alive()
        if self.stderr:
            alive = alive or self._stderr_thread.is_alive()
        return alive

    def _output_handler(self):
        while self.__io_readers_alive() and not self._stop:
            self.process_output(lines=LINES_TO_GET, timeout=IO_WAIT)
            time.sleep(0.1)#IO_WAIT)

    def _start_background_io_reading(self):
        if self.stdout:
            self._stdout_thread.start()
        if self.stderr:
            self._stderr_thread.start()

    def _read(self, stream, queue):
        print "reading... ", stream
        for line in iter(stream.readline, ''):
            try:
                queue.put(line)
                if self._stop:
                    break
            except Full:
                #drop it :/
                print "Queue full for stream {0} of {1}".format(stream, self.name)
                print "Dropping line."

        stream.close()


    def _get_lines(self, stream, q, lines=None, timeout=None):
        lines = lines if lines else 1
        out = []
        for num in range(lines):
            try:
                if timeout:
                    line = q.get(block=True, timeout=timeout)
                else:
                    line = q.get(block=False)
            except Empty:
                return out
            else: # got line
                out.append(line)
        return out


    def _handle_stdout(self, lines=None, timeout=None):
        self._handle_stdio(self.stdout, self._out_q,
                            self._out_log, self.out_tail, lines, timeout)


    def _handle_stdio(self, stream, q, log, tail, lines=None, timeout=None):
        out = self._get_lines(stream, q, lines, timeout)
        tail.extend(out)
        if log is not None:
            try:
                log.writelines(out)
            except Exception, e:
                print e, e.args


    def _handle_stderr(self, lines=None, timeout=None):
        self._handle_stdio(self.stderr, self._err_q,
                            self._err_log, self.err_tail, lines, timeout)