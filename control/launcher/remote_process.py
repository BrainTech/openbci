#!/usr/bin/python
# -*- coding: utf-8 -*-

import zmq

from obci.control.common.message import OBCIMessageTool, PollingObject, send_msg, recv_msg
from obci.control.launcher.launcher_messages import message_templates

from process_io_handler import DEFAULT_TAIL_RQ

import process
from process import FAILED, FINISHED, TERMINATED, UNKNOWN, NON_RESPONSIVE,\
PING, RETURNCODE, REG_TIMER

class RemoteProcess(process.Process):
    def __init__(self, proc_description, rq_address,
                                reg_timeout_desc=None,
                                monitoring_optflags=PING,
                                logger=None):

        self.rq_address = rq_address
        self._ctx = None
        # returncode monitoring is not supported in remote processes..
        monitoring_optflags = monitoring_optflags & ~(1 << RETURNCODE)

        super(RemoteProcess, self).__init__(proc_description,
                                        reg_timeout_desc, monitoring_optflags,
                                        logger)


    def is_local(self):
        return False

    def _do_handle_timeout(self, type_):
        if type_ == REG_TIMER:
            self._status = FAILED
            self._status_details = "Failed to register before timeout."

    def registered(self, reg_data):
        super(RemoteProcess, self).registered(reg_data)
        self.desc.pid = reg_data.pid

    def returncode_monitor(self):
        pass

    def kill(self):
        #send "kill" to the process or kill request to its supervisor?
        self.stop_monitoring()
        if not self._ctx:
            self._ctx = zmq.Context()
        rq_sock = self._ctx.socket(zmq.REQ)
        rq_sock.connect(self.rq_address)
        mtool = OBCIMessageTool(message_templates)
        poller = PollingObject()
        send_msg(rq_sock, mtool.fill_msg("kill_process", pid=self.pid, machine=self.machine_ip))
        res, _ = poller.poll_recv(rq_sock, timeout=5000)
        if res:
            res = mtool.unpack_msg(res)
            print "Response to kill request: ", res

            with self._status_lock:
                self._status = TERMINATED
