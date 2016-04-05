#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import subprocess
import sys
import os
import socket

import zmq

from obci.control.common.message import OBCIMessageTool, PollingObject, send_msg
from obci.control.launcher.launcher_messages import message_templates

from obci.utils.openbci_logging import get_logger

from process_io_handler import start_stdio_handler
from local_process import LocalProcess
from remote_process import RemoteProcess
from process import FAILED, FINISHED, TERMINATED, UNKNOWN,\
    PING, RETURNCODE


NO_STDIO = 0
STDOUT = 1
STDERR = 2
STDIN = 4

STDIO = [NO_STDIO, STDOUT, STDERR, STDIN]

PYTHON_CALL = ['python']  # , '-u']

REGISTER_TIMEOUT = 3

_DEFAULT_TIMEOUT = 20
_DEFAULT_TIMEOUT_MS = 6000


class SubprocessMonitor(object):

    def __init__(self, zmq_ctx, uuid, logger=None, obci_dns=None):
        self._processes = {}
        self._ctx = zmq_ctx
        self.uuid = uuid
        self.logger = logger or get_logger('subprocess_monitor',
                                           stream_level='warning')
        self.obci_dns = obci_dns
        self._mtool = OBCIMessageTool(message_templates)
        self.poller = PollingObject()
        self._proc_lock = threading.RLock()

    def not_running_processes(self):
        status = {}
        with self._proc_lock:
            for key, proc in self._processes.iteritems():
                st = proc.status()
                if st[0] in [FINISHED, FAILED, TERMINATED] and not proc.marked_delete():
                    status[key] = st

        return status

    def unknown_status_processes(self):
        with self._proc_lock:
            return [proc for proc in self._processes.values()
                    if proc.status()[0] == UNKNOWN]

    def process(self, machine_ip, pid):
        with self._proc_lock:
            return self._processes.get((machine_ip, pid), None)

    def killall(self, force=False):
        with self._proc_lock:
            for proc in self._processes.values():
                kill_method = proc.kill if not force else proc.kill_with_force
                if proc.status()[0] not in [FINISHED, FAILED, TERMINATED]:
                    kill_method()

    def delete(self, machine, pid):
        proc = self._processes.get((machine, pid), None)
        if proc is None:
            raise Exception("Process not found: " + str((machine, pid)))
        if not proc.running():
            del self._processes[(machine, pid)]
            return True
        else:
            self.logger.error("Process is running, will not delete! " + str((machine, pid)))
            return False

    def delete_all(self):
        with self._proc_lock:
            for proc in self._processes.values():
                del proc
            self._processes = {}

    def stop_monitoring(self):
        with self._proc_lock:
            for proc in self._processes.values():
                proc.stop_monitoring()

    def _launch_args(self, path, args):
        # TODO fix interpreter calls // only python is supported
        if path.endswith('.py'):
            launch_args = PYTHON_CALL + [path] + args
        else:
            launch_args = [path] + args
        return launch_args

    def _stdio_actions(self, io_flags):
        out = subprocess.PIPE if io_flags & STDOUT else None

        if io_flags & STDERR:
            err = subprocess.PIPE
        elif out is not None:
            err = subprocess.STDOUT
        else:
            err = None

        stdin = subprocess.PIPE if io_flags & STDIN else None
        return (out, err, stdin)

    def _local_launch(self, launch_args, stdio_actions, env):
        ON_POSIX = 'posix' in sys.builtin_module_names
        out, err, stdin = stdio_actions
        try:
            if sys.platform == "win32":
                crflags = subprocess.CREATE_NEW_PROCESS_GROUP
                popen_obj = subprocess.Popen(launch_args,
                                             stdout=out, stderr=err, stdin=stdin,
                                             bufsize=1, close_fds=ON_POSIX, env=env,
                                             creationflags=crflags)
            else:
                popen_obj = subprocess.Popen(launch_args,
                                             stdout=out, stderr=err, stdin=stdin,
                                             bufsize=1, close_fds=ON_POSIX, env=env)

            details = "Popen constructor finished for " +\
                str(launch_args[:3]) + "(...)"
            self.logger.info(details)
            return popen_obj, details
        except OSError as e:
            details = "Unable to spawn process {0} [{1}]".format(launch_args, e.args)
            self.logger.error(details)
            return None, details
        except ValueError as e:
            details = "Unable to spawn process (bad arguments) {0} [{1}]".format(launch_args, e.args)
            self.logger.error(details)
            return None, details
        except Exception as e:
            details = "Process launch Error: " + str(e) + str(e.args) + str(vars(e))
            self.logger.error(details)
            return None, details

    def new_local_process(self, path, args, proc_type='', name='',
                          capture_io=STDOUT | STDIN,
                          stdout_log=None,
                          stderr_log=None,
                          register_timeout_desc=None,
                          monitoring_optflags=RETURNCODE | PING,
                          machine_ip=None,
                          env=None):

        launch_args = self._launch_args(path, args)
        self.logger.debug(proc_type + " local path:  " + path)
        machine = machine_ip if machine_ip else socket.gethostname()
        std_actions = self._stdio_actions(capture_io)
        timeout_desc = register_timeout_desc

        self.logger.debug('process launch arg list:  %s', launch_args)
        popen_obj, details = self._local_launch(launch_args, std_actions, env)

        if popen_obj is None:
            return None, details

        if popen_obj.returncode is not None:
            det = "opened process already terminated" + popen_obj.communicate()
            self.logger.warning(det)

        if not name:
            name = os.path.basename(path)

        process_desc = ProcessDescription(proc_type=proc_type,
                                          name=name,
                                          path=path,
                                          args=args,
                                          machine_ip=machine,
                                          pid=popen_obj.pid)

        # io_handler will be None if no stdio is captured
        io_handler = start_stdio_handler(popen_obj, std_actions,
                                         ':'.join([machine, path, name]),
                                         stdout_log, stderr_log)

        new_proc = LocalProcess(process_desc, popen_obj, io_handler=io_handler,
                                reg_timeout_desc=timeout_desc,
                                monitoring_optflags=monitoring_optflags,
                                logger=self.logger)

        if monitoring_optflags & PING:
            new_proc._ctx = self._ctx

        with self._proc_lock:
            self._processes[(machine, popen_obj.pid)] = new_proc

        new_proc.start_monitoring()

        return new_proc, None

    def new_remote_process(self, path, args, proc_type, name,
                           machine_ip, conn_addr,
                           capture_io=STDOUT | STDIN,
                           stdout_log=None,
                           stderr_log=None,
                           register_timeout_desc=None,
                           monitoring_optflags=PING):
        """Send a request to conn_addr for a process launch. By default
        the process will be monitored with ping requests and locally by the
        remote peer."""

        timeout_desc = register_timeout_desc

        rq_message = self._mtool.fill_msg('launch_process',
                                          path=path,
                                          args=args, proc_type=proc_type,
                                          name=name,
                                          machine_ip=machine_ip,
                                          capture_io=capture_io,
                                          stdout_log=stdout_log,
                                          stderr_log=stderr_log)

        rq_sock = self._ctx.socket(zmq.REQ)

        try:
            rq_sock.connect(conn_addr)
        except zmq.ZMQError as e:
            det = "Could not connect to {0}, err: {1}, {2}".format(
                conn_addr, e, e.args)
            self.logger.error(det)
            return None, det

        self.logger.info("SENDING LAUNCH REQUEST  {0}  {1}  {2} {3}".format(
            machine_ip, _DEFAULT_TIMEOUT_MS, 'ms', conn_addr))

        send_msg(rq_sock, rq_message)
        result, details = self.poller.poll_recv(rq_sock, _DEFAULT_TIMEOUT_MS)

        rq_sock.close()

        if not result:
            details = details + "  [address was: {0}]".format(conn_addr)
            self.logger.error(details)
            return None, details
        else:
            result = self._mtool.unpack_msg(result)

        if result.type == 'rq_error':
            det = "REQUEST FAILED" + str(result.err_code) + ':' + str(result.details)
            self.logger.error(det)
            return None, det
        elif result.type == 'launched_process_info':
            self.logger.info("REQUEST SUCCESS  %s", result.dict())
            process_desc = ProcessDescription(proc_type=result.proc_type,
                                              name=result.name,
                                              path=result.path,
                                              args=args,
                                              machine_ip=result.machine,
                                              pid=result.pid)

            new_proc = RemoteProcess(process_desc, conn_addr,
                                     reg_timeout_desc=timeout_desc,
                                     monitoring_optflags=monitoring_optflags,
                                     logger=self.logger)

            if monitoring_optflags & PING:
                new_proc._ctx = self._ctx

            with self._proc_lock:
                self._processes[(result.machine, result.pid)] = new_proc

            new_proc.start_monitoring()

            return new_proc, None


class ProcessDescription(object):

    def __init__(self, proc_type, name, path, args, machine_ip, pid=None):
        self.proc_type = proc_type
        self.name = name
        self.uuid = None
        self.path = path
        self.args = args
        self.machine_ip = machine_ip
        self.pid = pid

    def dict(self):
        return dict(proc_type=self.proc_type,
                    name=self.name,
                    uuid=self.uuid,
                    path=self.path,
                    args=self.args,
                    machine_ip=self.machine_ip,
                    pid=self.pid)


class TimeoutDescription(object):

    def __init__(self, timeout=REGISTER_TIMEOUT, timeout_method=None,
                 timeout_args=[]):
        self.timeout = timeout
        self.timeout_method = timeout_method if timeout_method else \
            self.default_timeout_method
        self.timeout_args = timeout_args

    def default_timeout_method(self):
        return None

    def timer(self):
        return threading.Timer(self.timeout, self.timeout_method, self.timeout_args)


def default_timeout_handler():
    return TimeoutDescription()
