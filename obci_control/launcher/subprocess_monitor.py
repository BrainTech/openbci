#!/usr/bin/python
# -*- coding: utf-8 -*-

import threading
import common.obci_control_settings as settings
import common.net_tools as net
import subprocess
import sys
import time

from collections import deque
try:
    from Queue import Queue, Empty, Full
except ImportError:
    from queue import Queue, Empty, Full  # python 3.x

PING = 2
RETURNCODE = 4

MONITORING_OPTIONS = [PING, RETURNCODE]

NO_STDIO = 0
STDOUT = 1
STDERR = 2
STDIN = 4

STDIO = [NO_STDIO, STDOUT, STDERR, STDIN]

PYTHON_CALL = ['python', '-u']

REGISTER_TIMEOUT = 3
STDIO_QUEUE_MAX_SIZE = 8192
STDIO_TAIL_LEN = 128
DEFAULT_TAIL_RQ = 10

LINES_TO_GET = 5
IO_WAIT = 0.5

class SubprocessManager(object):
	def __init__(self):
		self.processes = []

	def new_local_process(self, path, args, proc_type='', proc_name='',
								capture_io= STDOUT | STDIN,
								stdout_log=None,
								stderr_log=None,
								must_register=True,
								monitoring_optflags=RETURNCODE | PING):

		if path.endswith('.py'):
			launch_args = PYTHON_CALL +[path] + args
		else:
			launch_args = [path] + args

		machine = net.ext_ip()
		out = subprocess.PIPE if capture_io & STDOUT else None
		print "out capture: ", capture_io & STDOUT, out

		if capture_io & STDERR:
			err = subprocess.PIPE
		elif out is not None:
			err = subprocess.STDOUT
		else: err = None
		print "err capt: ", capture_io & STDERR, err, subprocess.STDOUT

		stdin = subprocess.PIPE if capture_io & STDIN else None

		if must_register:
			timeout_desc = TimeoutDescription()
		else: timeout_desc = None

		ON_POSIX = 'posix' in sys.builtin_module_names
		try:
			popen_obj = subprocess.Popen(launch_args,
										stdout=out, stderr=err, stdin=stdin,
										bufsize=1, close_fds=ON_POSIX)
		except:
			print "Popen ERROR!!! {0}".format(path)
			raise
		else:

			process_desc = ProcessDescription(proc_type=proc_type,
											name=proc_name,
											path=path,
											args=args,
											machine_ip=machine,
											pid=popen_obj.pid)

			if out is not None or stdin is not None:
				out_handle = popen_obj.stdout if out is not None else None
				if err == subprocess.STDOUT or err is None:
					err_handle = None
				else: err_handle = popen_obj.stderr
				print "out: ", out_handle, "err: ", err_handle
				in_handle = popen_obj.stdin if stdin is not None else None

				#io_handler = None
				io_handler = ProcessIOHandler(
								name=':'.join([machine, path, proc_name]),
								stdout=out_handle,
								stderr=err_handle,
								stdin=in_handle,
								out_log=stdout_log, err_log=stderr_log)
				io_handler.start_output_handler()

				return LocalProcess(process_desc, popen_obj, io_handler=io_handler,
								must_register=must_register,
								reg_timeout_desc=timeout_desc,
								monitoring_optflags=monitoring_optflags)


	def new_remote_process(self, path, args, rq_socket, machine,
								must_register=True,
								monitoring_optflags=PING):
		pass



UNKNOWN = 'unknown'
RUNNING = 'running'
FAILED = 'failed'
FINISHED = 'finished'
NON_RESPONSIVE = 'non_responsive'

PROCESS_STATUS = [UNKNOWN, RUNNING, FAILED, FINISHED, NON_RESPONSIVE]

_REG_TIMER = 0

class Process(object):
	def __init__(self, proc_description,
								must_register=True,
								reg_timeout_desc=None,
								monitoring_optflags=PING):
		self._desc = proc_description
		self.proc_type = self._desc.proc_type

		self.status = UNKNOWN
		self.status_details = None

		self.must_register = must_register
		self.reg_timeout_desc = reg_timeout_desc if reg_timeout_desc else TimeoutDescription()
		self.reg_timer = None if not self.must_register else \
										self.new_timer(self.reg_timeout_desc)

		self.ping_it = monitoring_optflags & PING if self.must_register else False
		self.os_check_it = monitoring_optflags & RETURNCODE if \
										self._desc.pid is not None else False

		if self.must_register:
			self.reg_timer.start()


	def is_local(self):
		raise NotImplementedError()

	def timeout_handler(self, custom_method, args, type_):
		self._do_handle_timeout(type_)
		custom_method(args)

	def _do_handle_timeout(self, type_):
		raise NotImplementedError()

	def new_timer(self, tim_desc, type_):
		threading.Timer(self.timeout, self.timeout_handler,
							[tim_desc.timeout_method, tim_desc.timeout_args, type_])

	def registered(self, **kwargs):
		self.status = RUNNING
		self.reg_timer.cancel()

	def check_status(self):
		raise NotImplementedError()



class LocalProcess(Process):
	def __init__(self, proc_description, popen_obj, io_handler=None,
								must_register=True,
								reg_timeout_desc=None,
								monitoring_optflags=PING | RETURNCODE):
		self.popen_obj = popen_obj
		self.io_handler = io_handler

		super(LocalProcess, self).__init__(proc_description, must_register,
										reg_timeout_desc, monitoring_optflags)

	def is_local(self):
		return True

	def _do_handle_timeout(self, type_):
		if type_ == _REG_TIMER:
			self.status = FAILED
			self.status_details = "Failed to register before timeout."
			self.popen_obj.kill()

	def tail_stdout(self, lines=DEFAULT_TAIL_RQ):
		if not self.io_handler:
			return None
		else:
			return self.io_handler.tail_stdout(lines)

	def kill(self):
		if self.popen_obj.returncode is None:
			self.popen_obj.kill()



class RemoteProcess(Process):
	def __init__(self, proc_description, launch_rq_result, rq_socket,
								must_register=True,
								reg_timeout_desc=None,
								monitoring_optflags=PING):

		self.launch_rq_result = launch_rq_result
		self.launch_rq_socket = rq_socket
		super(RemoteProcess, self).__init__(proc_description, must_register,
										reg_timeout_desc, monitoring_optflags)


	def is_local(self):
		return False

	def _do_handle_timeout(self, type_):
		if type_ == _REG_TIMER:
			self.status = FAILED
			self.status_details = "Failed to register before timeout."


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

		print "OUTTT: ", self._out_q, self._stdout_thread, self._out_log


		self.out_tail = deque(maxlen=STDIO_TAIL_LEN)
		self.err_tail = deque(maxlen=STDIO_TAIL_LEN)


		self._err_q, self._stderr_thread, self._err_log = \
									self.__init_io(self.stderr, err_log)
		print "ERRR: ", self._err_q, self._stderr_thread, self._err_log

		if self.stdout or self.stderr:
			self._start_background_io_reading()

	def __init_io(self, stream, log_name):

		q, thr, log = None, None, None
		if stream is not None:
			q = Queue(maxsize=STDIO_QUEUE_MAX_SIZE)
			thr = threading.Thread(target=self._read, args=(stream, q))
			#thr.daemon = True

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
				print "deque empty"
				break
		return data

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

	def __io_readers_alive(self):
		alive = False
		if self.stdout:
			alive = self._stdout_thread.is_alive()
		if self.stderr:
			alive = alive or self._stderr_thread.is_alive()
		return alive

	def _output_handler(self):
		while self.__io_readers_alive() and not self._stop:
			self.process_output(lines=LINES_TO_GET)
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
				print "aaaa", line
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
				print line
		return out

	def _handle_stdout(self, lines=None, timeout=None):
		self._handle_stdio(self.stdout, self._out_q,
							self._out_log, self.out_tail, lines, timeout)

	def _handle_stdio(self, stream, q, log, tail, lines=None, timeout=None):
		out = self._get_lines(stream, q, lines, timeout)
		print "got out:", out
		tail.extend(out)
		if log is not None:
			try:
				log.writelines(out)
			except Error, e:
				print e, e.args

	def _handle_stderr(self, lines=None, timeout=None):
		self._handle_stdio(self.stderr, self._err_q,
							self._err_log, self.err_tail, lines, timeout)


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
