#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, socket

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_client import ConfiguredClient

from configs import settings, variables_pb2
from drivers import drivers_logging as logger

LOGGER = logger.get_logger("etr_calibration", "info")

class EtrCalibration(ConfiguredClient):
    """A simple class to convey data from multiplexer (UGM_UPDATE_MESSAGE)
    to ugm_engine using udp. That level of comminication is needed, as
    pyqt won`t work with multithreading..."""
    def __init__(self, addresses):
        super(EtrCalibration, self).__init__(addresses=addresses, type=peers.ETR_CALIBRATION)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.get_param('rcv_ip'),int(self.get_param('rcv_port'))))
        self.socket.listen(1)
        LOGGER.info("Start initializin etr amplifier...")
        print "\n"*10 
        print "STARTING ETR CALIBRATION"
        print "\n"*10
        self.ready()

    def run(self):
        print "\n"*10 
        print "RUNNNING ETR CALIBRATION"
        print "\n"*10 
        try:
            while True:
                print "*"*10
                print "socket"
                conn, addr = self.socket.accept()
                l_data = conn.recv(1024)
                print "*"*10
                print "l_data: ", l_data
                msg = variables_pb2.Variable()
                msg.ParseFromString(l_data)
                print "*"*10
                print "msg: ", msg.key, ' / ', msg.value
                print "*"*10
                #tu pewnie będzie czytanie obrazu z kamery i po otrzymaniu info o stopie kalibracji
                #pewnie bedzie odpalenie send_results
        finally:
            self.socket.close()

    def _send_results(self):
        r = variables_pb2.Sample()
        r.timestamp = time.time()
        for i in range(8):
            r.channels.append(random.random())
        self.conn.send_message(message = r.SerializeToString(), 
                               type = types.ETR_CALIBRATION_RESULTS, flush=True)


if __name__ == "__main__":
    EtrCalibration(settings.MULTIPLEXER_ADDRESSES).run()
