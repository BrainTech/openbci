#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, sys

from obci.drivers.generic import py_amplifier
from obci.utils.openbci_logging import log_crash
from obci.utils import streaming_debug

class PyAmplifierSoft(py_amplifier.PyAmplifier):

    def _manage_params(self):
        super(PyAmplifierSoft, self)._manage_params()
        self._next_msg = None
        self._prev_ts = 0.0
        self._first_sample_ts = 0.0
        self.sleep_time =(1.0/float(self.get_param('sampling_rate')))*self.samples_per_packet
        self.debug = streaming_debug.Debug(int(self.config.get_param('sampling_rate')), 
                                           self.logger,
                                           self.samples_per_packet)

    def _get_msg(self):
        t = time.time()
        samples = []
        for i in range(self.samples_per_packet):
            s, ts = self._get_sample()
            if s is None:
                return s
            if ts is None:
                ts = t + i*(self.sleep_time/self.samples_per_packet)
            samples.append((s, ts))

        return self._create_msg(samples)

    def _get_mx_msg(self, msg=None):
        if msg is None:
            msg = self._get_msg()
            if msg is None:
                return None

        return self._create_mx_msg(msg)

    @log_crash            
    def do_sampling(self):
        msg = self._get_msg()
        self._first_sample_ts = msg.samples[0].timestamp
        self._next_mx_msg = self._get_mx_msg(msg)

        while True:
            self._prev_ts = time.time()
            self._send(self._next_mx_msg)
            self._next_mx_msg = self._get_mx_msg()
            if self._next_mx_msg is None:
                self.logger.info("No more samples. Abort amplifier...")
                break
            self._post_send()
            self.debug.next_sample()
            while (time.time() - self._prev_ts < self.sleep_time):
                time.sleep(0.001)
        sys.exit(0)

    def _get_sample(self):
        raise Exception("To be subclassed")

    def _post_send(self):
        pass

