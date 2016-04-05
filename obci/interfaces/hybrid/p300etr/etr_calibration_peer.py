#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, socket

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient

from obci.configs import settings, variables_pb2
from cam import Camera
from obci.utils.openbci_logging import log_crash

class EtrCalibration(ConfiguredClient):
    """A simple class to convey data from multiplexer (UGM_UPDATE_MESSAGE)
    to ugm_engine using udp. That level of comminication is needed, as
    pyqt won`t work with multithreading..."""
    @log_crash
    def __init__(self, addresses):
        super(EtrCalibration, self).__init__(addresses=addresses, type=peers.ETR_CALIBRATION)
        
        HOST = self.get_param('rcv_ip')
        PORT = int(self.get_param('rcv_port'))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST,PORT))
        self.socket.listen(1)
        self.conn, addr = self.socket.accept()
        self.ready()
        self.logger.info("Start initializin etr amplifier...")
        
        self.init()
        self.initCamera()

    def __del__(self):
        self.socket.close()
        
    def init():
        self._treshold = 200
        self.invMatrix = np.eye(3)
        
    def initCamera(self):
        self.cam = Camera()
        self.cam.setTreshold(self._treshold)

    def run(self):
        try:
            while True:

                l_data = self.conn.recv(1024)
                msg = variables_pb2.Variable()
                msg.ParseFromString(l_data)
                #~ msg.key, msg.value # jedno z nich to timestamp i start_calibration
                l_msg = None #tu bedzie parsowanie wiadomosci o starcie i koncu kalibracji
                if l_msg is not None:
                    pass
                
                #tu pewnie będzie czytanie obrazu z kamery i po otrzymaniu info o stopie kalibracji
                #pewnie bedzie odpalenie send_resultsc
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
