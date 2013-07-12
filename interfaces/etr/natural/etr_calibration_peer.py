#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, socket, subprocess, os

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_client import ConfiguredClient

from obci.configs import settings, variables_pb2
from obci.utils.openbci_logging import log_crash

#~ from camera import Camera
import numpy as np

#~ from threading import Thread
#~ 
#~ class Cam(Thread):
    #~ def run(self):
        #~ self.cam = Camera()

class EtrCalibration(ConfiguredClient):
    """A simple class to convey data from multiplexer (UGM_UPDATE_MESSAGE)
    to ugm_engine using udp. That level of comminication is needed, as
    pyqt won`t work with multithreading..."""
    @log_crash
    def __init__(self, addresses):
        super(EtrCalibration, self).__init__(addresses=addresses, type=peers.ETR_CALIBRATION)
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.get_param('rcv_ip'),int(self.get_param('rcv_port'))))
        self.socket.listen(1)
        self.ready()
        self.logger.info("Start initializin etr amplifier...")
        
        #~ self.thread = Cam()
        #~ self.thread.run()
        
        self.logger.info("\n"*10 +"I don't fancy you"+ "\n"*10)

    def __del__(self):
        self.socket.close()        

    def run(self):
        try:
            while True:
                
                conn, addr = self.socket.accept()
                l_data = conn.recv(1024)
                msg = variables_pb2.Variable()
                msg.ParseFromString(l_data)
                os.system("touch " + os.path.expanduser("~/obci/interfaces/etr/natural/calibFlag"))
                time.sleep(0.4)
                print "\n"*10 + "*"*10 + "\n"*10
                print "msg: ", msg.key, ' / ', msg.value
                #~ l_msg = None #tu bedzie parsowanie wiadomosci o starcie i koncu kalibracji
                #~ if l_msg is not None:
                    #~ pass

                self.invH = np.load(os.path.expanduser("~/obci/interfaces/etr/natural/calibMat.npy"))
                print self.invH
                #~ self.invH = self.calibrationStart()
                #~ self.invH = self.fakeMatrix()
                self._send_results()

        finally:
            self.socket.close()

    def fakeMatrix(self):
        return np.vstack((np.random.random((2,3)), np.array([[0,0,1]])))
    
    def _send_results(self):
        r = variables_pb2.Sample()
        r.timestamp = time.time()
        for val in self.invH.flatten().tolist():
            r.channels.append(val)
        self.logger.info("sending matrix: " + str(self.invS.flatten().tolist()) )
        print "types.ETR_CALIBRATION_RESULTS: ", types.ETR_CALIBRATION_RESULTS
        self.conn.send_message(message = r.SerializeToString(), 
                               type = types.ETR_CALIBRATION_RESULTS, flush=False)


if __name__ == "__main__":
    subprocess.Popen(["python", "/home/brain/obci/interfaces/etr/natural/camera.py"])
    EtrCalibration(settings.MULTIPLEXER_ADDRESSES).run()
