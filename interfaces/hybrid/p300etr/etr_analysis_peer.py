#!/usr/bin/env python
# -*- coding: utf-8 -*-


from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from configs import settings, variables_pb2
import random, time, sys

from interfaces import interfaces_logging as logger

import numpy as np

LOGGER = logger.get_logger("etr_analysis", "info")


class EtrAnalysis(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(EtrAnalysis, self).__init__(addresses=addresses,
                                     type=peers.ETR_P300_ANALYSIS)
                                     
        self.initConstants()
        self.ready()

    def initConstants(self):
        """
        Initiates constants values.
        """
        self.areaCount = int(self.get_param('speller_area_count'))
        print "self.areaCount: ", self.areaCount
        
        bufforLen = 10
        self.buffor = np.zeros((2,bufforLen))
        self.metricBuffor = np.zeros((self.areaCount, bufforLen))

    def metric(self, xy):
        """
        Measures metric in squares space.
        """
        m = np.zeros(self.areaCount)
        # For each square calc distance from present xy
        #~ for i, s in enumerate(squares):
            #~ m[i] = np.sqrt(np.dot(xy,s.xy))
            
        return m

    def _update_heatmap(self, m):
        """
        Updates values of heatmap and creates probabilty 
        density for each epoch.
        """
        m = m[np.newaxis].T
        self.metricBuffor = np.concatenate( (self.metricBuffor, m), axis=1)[:,1:]
    
    def _calc_pdf(self):
        self.pdf = np.sum(self.metricBuffor, axis=1)
        self.pdf = self.pdf/np.sum(self.pdf)
        return self.pdf
    
    def _update_buffor(self, xy):
        """
        Updates buffor of gaze values.
        """
        self.buffor = np.concatenate( (self.buffor, xy), axis=1)[:,1:]
    
    def handle_message(self, mxmsg):
        LOGGER.info("EtrAnalysis\n")
        if mxmsg.type == types.ETR_CALIBRATION_RESULTS:
        #### What to do when receive ETR_MATRIX information
            res = variables_pb2.Sample()
            res.ParseFromString(mxmsg.message)
            LOGGER.debug("GOT ETR CALIBRATION RESULTS: "+str(res.channels))


        elif mxmsg.type == types.ETR_SIGNAL_MESSAGE:
        #### What to do when receive ETR_SIGNAL information
            l_msg = variables_pb2.Sample2D()
            l_msg.ParseFromString(mxmsg.message)
            #~ LOGGER.debug("GOT MESSAGE: "+str(l_msg))
            
            
            # Change shape of data  
            x, y = l_msg.x, l_msg.y
            xy = np.array([[x],[y]])
            
            self._update_buffor(xy)
            
            # Caunt metric
            m = self.metric(xy)
            self._update_heatmap(m)
            
            # Calc heatmap as probabilty density
            #~ pdf = self._calc_pdf()
            
            ##self.conn.send_message(message = str(dec), type = types.DECISION_MESSAGE, flush=True)
            self._send_results()

        elif mxmsg.type == types.BLINK_MESSAGE:
        #### What to do when receive BLINK_NO information
            blink = variables_pb2.Blink()
            blink.ParseFromString(mxmsg.message)
            LOGGER.debug("GOT BLINK: "+str(blink.index)+" / "+str(blink.timestamp))
            

        self.no_response()

    def _send_results(self):
        """
        Sends results do decision making module.
        """
        tmpVal = np.random.random(8)
        print "Przesylam: ", tmpVal
        
        r = variables_pb2.Sample()
        r.timestamp = time.time()
        for i in range(8):
            r.channels.append(tmpVal[i])
        self.conn.send_message(message = r.SerializeToString(), type = types.ETR_ANALYSIS_RESULTS, flush=True)


if __name__ == "__main__":
    EtrAnalysis(settings.MULTIPLEXER_ADDRESSES).loop()

