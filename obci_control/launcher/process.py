#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import time

import zmq

from common.message import OBCIMessageTool, PollingObject, send_msg
from launcher_messages import message_templates

from utils.openbci_logging import get_logger

UNKNOWN = 'unknown'
RUNNING = 'running'
FAILED = 'failed'
FINISHED = 'finished'
TERMINATED = 'terminated'
NON_RESPONSIVE = 'non_responsive'

PROCESS_STATUS = [UNKNOWN, RUNNING, FAILED, FINISHED, TERMINATED, NON_RESPONSIVE]

PING = 2
RETURNCODE = 4

MONITORING_OPTIONS = [PING, RETURNCODE]


REG_TIMER = 0

class Process(object):
    def __init__(self, proc_description,
                                reg_timeout_desc=None,
                                monitoring_optflags=PING,
                                logger=None):

        self.desc = proc_description

        self.must_register = reg_timeout_desc is not None
        self._status_lock = threading.RLock()
        self._status = UNKNOWN if self.must_register else RUNNING
        self._status_details = None

        self.ping_it = monitoring_optflags & PING
        self.check_returncode = monitoring_optflags & RETURNCODE if \
                                        self.desc.pid is not None else False

        self.logger = logger or get_logger(
                                'subprocess_monitor'+'-'+self.desc.name+'-'+str(self.desc.pid),
                                stream_level='info')
        self.set_registration_timeout_handler(reg_timeout_desc)
        self.registration_data = None

        self._stop_monitoring = False
        self._ping_thread = None
        self._ping_retries = 8
        self._returncode_thread = None
        self._mtool = OBCIMessageTool(message_templates)
        self._ctx = None
        self.rq_sock = None
        self._poller = PollingObject()

        self.delete = False


    @property
    def machine_ip(self):
        return self.desc.machine_ip

    @property
    def pid(self):
        return self.desc.pid

    @property
    def path(self):
        return self.desc.path

    @property
    def proc_type(self):
        return self.desc.proc_type

    @property
    def name(self):
        return self.desc.name

    def status(self):
        with self._status_lock:
            return self._status, self._status_details

    def set_registration_timeout_handler(self, reg_timeout_desc):
        with self._status_lock:
            self._status = UNKNOWN
            self._status_details = None
        self.must_register = reg_timeout_desc is not None
        self.reg_timeout_desc = reg_timeout_desc
        self.reg_timer = None if not self.must_register else \
                                        self.new_timer(self.reg_timeout_desc, REG_TIMER)

        if self.must_register:
            self.reg_timer.start()

    def is_local(self):
        raise NotImplementedError()

    def timeout_handler(self, custom_method, args, type_):
        self._do_handle_timeout(type_)
        custom_method(*args)

    def _do_handle_timeout(self, type_):
        raise NotImplementedError()

    def new_timer(self, tim_desc, type_):
        return threading.Timer(tim_desc.timeout, self.timeout_handler,
                            [tim_desc.timeout_method, tim_desc.timeout_args, type_])

    def registered(self, reg_data):
        if self.reg_timer is not None:
            self.reg_timer.cancel()

        self.logger.info("{0} [{1}]  REGISTERED!!! {2}".format(
                                            self.name, self.proc_type, reg_data.machine_ip))
        #print "ping:", self.ping_it, "ret:", self.check_returncode
        with self._status_lock:
            self._status = RUNNING
        #TODO validate registration data
        self.registration_data = reg_data
        if self.ping_it:
            if not self._ctx:
                self._ctx = zmq.Context()
            self.rq_sock = self._ctx.socket(zmq.REQ)
            for addr in reg_data.rep_addrs:
                self.rq_sock.connect(addr)


    def stop_monitoring(self):
        if self.reg_timer:
            self.reg_timer.cancel()
            self.reg_timer = None
        self._stop_monitoring = True

        if self._ping_thread is not None:
            self.logger.info("%s, %s, %s",
                            self.proc_type, self.name ,"Joining ping thread")
            
            self._ping_thread.join()
        if self._returncode_thread is not None:
            self.logger.info("%s  %s  %s",
                            self.proc_type,self.name, "joining returncode thread")
            self._returncode_thread.join()
        self.logger.info("monitor for: %s, %s, %s", 
                    self.proc_type,self.name, "  ...monitoring threads stopped.")

    def finished(self):
        finished = True
        if self._ping_thread is not None:
            finished = not self._ping_thread.is_alive()
        if self._returncode_thread is not None:
            finished = finished and not self._returncode_thread.is_alive()
        return finished

    def process_is_running(self):
        running = True
        if self._ping_thread is not None:
            running = self._ping_thread.is_alive()
        if self._returncode_thread is not None:
            running = running and self._returncode_thread.is_alive()
        return running

    def start_monitoring(self):
        if self.ping_it:
            self._ping_thread = threading.Thread(target=self.ping_monitor, args=())
            self._ping_thread.daemon = True
            self._ping_thread.start()
        if self.check_returncode:
            self._returncode_thread = threading.Thread(target=self.returncode_monitor, args=())
            self._returncode_thread.daemon = True
            self._returncode_thread.start()

    def ping_monitor(self):
        is_alive = True
        while not self._stop_monitoring and is_alive:
            time.sleep(2)
            if self.rq_sock is not None:
                send_msg(self.rq_sock, self._mtool.fill_msg('ping'))
                result = None
                while self._ping_retries and not result and not self._stop_monitoring:
                    result, det = self._poller.poll_recv(socket=self.rq_sock, timeout=1500)
                if not result and not self._stop_monitoring:
                    self.logger.info("%s %s %s", 
                            self.proc_type, self.name, "NO RESPONSE TO PING!")
                    with self._status_lock:
                        if self._status not in [FAILED, FINISHED]:
                            self._status = NON_RESPONSIVE
                            self._status_details = 'ping response timeout'
                        print "status:", self._status
                        is_alive = False


    def returncode_monitor(self):
        raise NotImplementedError()

    def kill(self):
        raise NotImplementedError()

    def mark_delete(self):
        with self._status_lock:
            self.delete = True

    def marked_delete(self):
        with self._status_lock:
            return self.delete