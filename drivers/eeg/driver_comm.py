#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os.path
import subprocess
import signal
import time
import socket

from drivers import drivers_logging as logger
from launcher.launcher_tools import obci_root

from subprocess import Popen
from threading  import Thread

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x


LOGGER = logger.get_logger("DriverComm", "info")
SEP = ';'

class DriverComm(object):
    """ Start, stop and communicate with amplifier driver binaries. 
        Note: To run amplifier as OBCI experiment peer, use subclasses of BinaryDriverWrapper
        which fully support INI file configuration.

        Example:
        >>> from peer.peer_config import PeerConfig
        >>> import json

        >>> conf = PeerConfig('amplifier')
        >>> conf.add_local_param('driver_executable', 'drivers/eeg/cpp_amplifiers/dummy_amplifier')
        >>> conf.add_local_param('samples_per_packet', '4')

        >>> driv = DriverComm(conf)
        >>> descr = driv.get_driver_description() # channels_info
        >>> dic = json.loads(descr)
        >>> driv.start_sampling()
        >>> time.sleep(3)
        >>> driv.terminate_driver()
    """
    
    def __init__(self, peer_config, mx_addresses=[('localhost', 41921)], catch_signals=True):
        """ *peer_config* - parameter provider. Should respond to get_param(param_name, value)
        and has_param(param_name) calls. PeerConfig and PeerControl objects are suitable.
        *mx_addresses* - list of (host, port) pairs. Port value None means using default
        amplifier binary value.
        """
        self.config = peer_config
        if not hasattr(self, "_mx_addresses"):
            # FIXME
            self._mx_addresses = mx_addresses
        if not hasattr(self, "logger"):
            self.logger = LOGGER
        self.driver = self.run_driver(self.get_run_args((socket.gethostbyname(
                                self._mx_addresses[0][0]), self._mx_addresses[0][1])))
        self.driver_out_q = Queue()
        self.driver_out_thr = Thread(target=enqueue_output,
                                    args=(self.driver.stdout, self.driver_out_q))
        self.driver_out_thr.daemon = True # thread dies with the program
        self.driver_out_thr.start()

        self.driver_err_q = Queue()
        self.driver_err_thr = Thread(target=enqueue_output,
                                    args=(self.driver.stderr, self.driver_err_q))
        self.driver_err_thr.daemon = True # thread dies with the program
        self.driver_err_thr.start()


        if catch_signals:
            signal.signal(signal.SIGTERM, self.signal_handler())
            signal.signal(signal.SIGINT, self.signal_handler())

    def signal_handler(self):
        def handler(signum, frame):
            self.logger.info("Got signal " + str(signum) + "!!! Stopping driver!")
            self.stop_sampling()
            self.terminate_driver()
            self.logger.info("Exit!")
            sys.exit(-signum)
        return handler

    def run_driver(self, run_args):        
        self.logger.info("Executing: "+' '.join(run_args))
        return Popen(run_args,stdin=subprocess.PIPE,stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def get_driver_description(self):
        return self._communicate()

    def set_driver_params(self):
        self.set_sampling_rate(self.config.get_param("sampling_rate"))
        self.set_active_channels(self.config.get_param("active_channels"))

    def get_run_args(self,multiplexer_address):
        host,port=multiplexer_address

        exe=self.config.get_param('driver_executable')
        exe=os.path.join(obci_root(), exe)
        print exe
        args = [exe, '-v', self.config.get_param('samples_per_packet')]

        if port:
            args += ["-h",str(host),'-p',str(port)]

        if self.config.has_param("usb_device") and self.config.has_param("bluetooth_device"):
            usb = self.config.get_param("usb_device")
            if usb:
                args.extend(["-d", usb])
            elif self.config.get_param("bluetooth_device"):
                args.extend(["-b", self.config.get_param("bluetooth_device")])
            else:
                raise Exception("usb_device or bluetooth_device is required")
        
        if self.config.has_param("amplifier_responses"):
            if self.config.get_param("amplifier_responses"):
                args.extend(["-r", self.config.get_param("amplifier_responses")])
        if self.config.has_param("dump_responses"):
            if self.config.get_param("dump_responses"):
                args.extend(["--save_responses", self.config.get_param("dump_responses")])
        return args

    def set_sampling_rate(self,sampling_rate):
        self.logger.info("Set sampling rate: %s "%sampling_rate)
        error=self._communicate("sampling_rate "+str(sampling_rate),
                                    timeout_s=2, timeout_error=False)
        if error:
            print error

    def set_active_channels(self,active_channels):
        self.logger.info("Set Active channels: %s"%active_channels)
        error=self._communicate("active_channels "+str(active_channels),
                                    timeout_s=2, timeout_error=False)
        if error:
            print error

    def start_sampling(self):
        signal.signal(signal.SIGINT, self.stop_sampling)
        self.logger.info("Start sampling")
        error=self._communicate("start",  timeout_s=0, timeout_error=False)
        if error:
            print error
        self.logger.info("Sampling started")

    def stop_sampling(self,_1=None,_2=None):
        # sys.stderr.write("stop sampling")
        self.logger.info("Stop sampling")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.driver.send_signal(signal.SIGINT)
        self.logger.info("Sampling stopped")

    def terminate_driver(self):
        self.driver.send_signal(signal.SIGTERM)
        self.driver.wait()
        self.logger.info("Terminated driver.")

    def abort(self, error_msg):
        time.sleep(2)
        self.logger.error(error_msg)
        if self.driver_is_running():
            self.logger.info("Stopping driver.")
            self.stop_sampling()
        if self.driver_is_running():
        #TODO does 'stop_sampling' always terminate the driver process???
            self.logger.info("driver still not dead")
            self.terminate_driver()
        sys.exit(1)

    def driver_is_running(self):
        self.driver.poll()
        return self.driver.returncode is None

    def _communicate(self,command="", timeout_s=7, timeout_error=True):
        if not self.driver_is_running():
            self.logger.error("Driver is not running!!!!!!!")
            sys.exit(self.driver.returncode)

        get_timeout = .1
        count = 0
        out=""
        self.driver.stdin.write(command+"\n")
        while timeout_s - get_timeout * count >= 0:
            line = None
            try:  line = self.driver_out_q.get(timeout=get_timeout) # or self.driver_out_q.get_nowait()
            except Empty:
                count += 1
                time.sleep(get_timeout)
                pass
            if line is None:
                continue
            elif len(line) == 0:
                self.abort("Got empty string from driver. ABORTING...!!!")
            elif line=="\n":
                break
            else:
                count = 0
                out+=line;

        if out == "" and timeout_error:
            self.abort("Communication with driver unsuccesful, \
timeout " + str(timeout_s) + "s passed. ABORTING!!!")
        return out

    def do_samplingg(self):
        self.driver.wait()
        self.logger.info("Driver finished working with code " + str(self.driver.returncode))
        sys.exit(self.driver.returncode)

    def do_sampling(self):
        self.logger.info("Stat waiting on drivers output....")
        while True: #read and log data from sterr and stoout of the driver...
            try:
                v = self.driver_err_q.get_nowait()
                self.logger.info(v)
            except Empty:
                pass
            try:
                v = self.driver_out_q.get_nowait()
                self.logger.info(v)
            except Empty:
                time.sleep(0.1)
        sys.exit(self.driver.returncode)



def enqueue_output(out, queue):
    for line in iter(out.readline, ''):
        queue.put(line)
    out.close()


if __name__ == "__main__":
    from peer.peer_config import PeerConfig
    import json

    conf = PeerConfig('amplifier')
    conf.add_local_param('driver_executable', 'drivers/eeg/cpp_amplifiers/tmsi_amplifier')
    conf.add_local_param('samples_per_packet', '4')
    conf.add_local_param('bluetooth_device', '')
    conf.add_local_param('usb_device', '/dev/tmsi0')

    driv = DriverComm(conf)
    descr = driv.get_driver_description()
    dic = json.loads(descr)
    driv.start_sampling()
    time.sleep(3)
    driv.terminate_driver()
