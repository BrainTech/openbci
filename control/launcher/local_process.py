#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import signal
import sys
from process_io_handler import DEFAULT_TAIL_RQ

import process
from process import FAILED, FINISHED, TERMINATED, UNKNOWN, NON_RESPONSIVE,\
PING, RETURNCODE, REG_TIMER


class LocalProcess(process.Process):
    def __init__(self, proc_description, popen_obj, io_handler=None,
                                reg_timeout_desc=None,
                                monitoring_optflags=PING | RETURNCODE,
                                logger=None):
        self.popen_obj = popen_obj
        self.io_handler = io_handler

        super(LocalProcess, self).__init__(proc_description,
                                        reg_timeout_desc, monitoring_optflags,
                                        logger)

    def is_local(self):
        return True

    def _do_handle_timeout(self, type_):
        if type_ == REG_TIMER:
            with self._status_lock:
                self._status = FAILED
                self._status_details = "Failed to register before timeout."

            self.kill()

    def tail_stdout(self, lines=DEFAULT_TAIL_RQ):
        if not self.io_handler:
            return None
        else:
            return self.io_handler.tail_stdout(int(lines))

    def kill(self):
        self.stop_monitoring()

        if self.io_handler is not None:
            if self.io_handler.is_running():
                self.io_handler.stop_output_handler()

        self.popen_obj.poll()
        with self._status_lock:
            if self.popen_obj.returncode is None:
                self.popen_obj.terminate()
            self.popen_obj.wait()

            if not self._status == NON_RESPONSIVE:
                self._status_details = -(self.popen_obj.returncode)
            self._status = TERMINATED

    def kill_with_force(self, timeout_s=0.1):
        self.stop_monitoring()

        if self.io_handler is not None:
            if self.io_handler.is_running():
                self.io_handler.stop_output_handler()

        self.popen_obj.poll()
        with self._status_lock:
            if self.popen_obj.returncode is None:
                if sys.platform == "win32":
                    self.logger.info("[win] sending CTRL_C_EVENT.............. %s", self.name)
                    self.popen_obj.send_signal(signal.CTRL_C_EVENT)
                else:
                    self.popen_obj.terminate()
        time.sleep(timeout_s)
        self.popen_obj.poll()
        with self._status_lock:
            if self.popen_obj.returncode is None:
                if sys.platform == "win32":
                    self.logger.info("[win] terminating process %s", self.name)
                    self.popen_obj.terminate()
                else:
                    self.logger.info("KILLING -9 PROCESS %s %s", self.pid, self.name)
                    self.popen_obj.send_signal(signal.SIGKILL)
            self.popen_obj.wait()
            if not self._status == NON_RESPONSIVE:
                self._status_details = -(self.popen_obj.returncode)
            self._status = TERMINATED




    def returncode_monitor(self):
        # TODO just use wait() instead of poll()ing every 0.5s
        # self.popen_obj.wait()
        # code = self.popen_obj.returncode


        # print "[subprocess_monitor]",self.proc_type,"process", \
        #                 self.name, "pid", self.pid, "ended with", code
        # with self._status_lock:

        #     if code == 0:
        #         self._status = FINISHED
        #         self._status_details = ''
        #     elif code < 0:
        #         self._status = TERMINATED
        #         self._status_details = -code
        #     else:
        #         self._status = FAILED
        #         self._status_detals = self.tail_stdout(15)

        while not self._stop_monitoring:
            self.popen_obj.poll()
            code = self.popen_obj.returncode

            if code is not None:
                self.logger.info(self.proc_type + " process " + self.name +\
                                    " pid " + str(self.pid) + " ended with " + str(code))
                with self._status_lock:
                    self.popen_obj.wait()
                    if code == 0:
                        self._status = FINISHED
                        self._status_details = ''
                    elif code < 0:
                        self._status = TERMINATED
                        self._status_details = -code
                    else:
                        self._status = FAILED
                        self._status_detals = self.tail_stdout(15)
                break
            elif self.status()[0] == NON_RESPONSIVE:
                self.logger.warning(self.proc_type + "process" + self.name +\
                                         "pid" + self.pid + "is NON_RESPONSIVE")
                with self._status_lock:
                    self.popen_obj.poll()
                    if self.popen_obj.returncode is None:
                        self.popen_obj.terminate()
                        self._status = TERMINATED
                    self.popen_obj.wait()
            else:
                time.sleep(0.5)
        #print "[subprocess_monitor]",self.proc_type,self.name, self.pid,\
        #                             self.popen_obj.returncode, self._stop_monitoring
        if self.popen_obj.returncode is not None:
            self.popen_obj.wait()

    def finished(self):
        finished = True
        if self._ping_thread is not None:
            finished = not self._ping_thread.is_alive()
        if self._returncode_thread is not None:
            finished = not self._returncode_thread.is_alive()
        return finished and self.popen_obj.returncode is not None

    def process_is_running(self):
        running = True
        if self._ping_thread is not None:
            running = self._ping_thread.is_alive()
        if self._returncode_thread is not None:
            running = running and self._returncode_thread.is_alive()
        return running and self.popen_obj.returncode is None