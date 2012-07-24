#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from configs import settings, variables_pb2
import random, time, sys
import numpy as np
import scipy.stats as st

from interfaces import interfaces_logging as logger
from gui.ugm import ugm_helper

LOGGER = logger.get_logger("p300_etr_decision", "info")


class P300EtrDecision(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(P300EtrDecision, self).__init__(addresses=addresses,
                                     type=peers.RESULTS_ANALYSIS)        

        self.initConst()
        self.initFile()
        self.ready()    
    
    def initConst(self):
        
        self.rows = int(self.config.get_param("rows"))
        self.cols = int(self.config.get_param("cols"))
        
        self.thresholdPercent = float(self.config.get_param("p300etr_threshold"))
        self.p300Tr =  float(self.config.get_param("p300_threshold"))
        self.etrTr =  float(self.config.get_param("etr_threshold"))
        
        self.pdf_p300 = np.zeros(self.rows*self.cols)
        self.pdf_etr = np.zeros(self.rows*self.cols)
        

    def handle_message(self, mxmsg):
        LOGGER.debug("P300EtrDecision\n")
        if mxmsg.type == types.ETR_ANALYSIS_RESULTS:
            res = variables_pb2.Sample()
            res.ParseFromString(mxmsg.message)
            LOGGER.debug("GOT ETR ANALYSIS RESULTS: "+str(res.channels))
    
            self.pdf_etr = np.array(res.channels)
            LOGGER.debug("pdf_etr: " + str(self.pdf_etr) )

            #self.conn.send_message(message = str(dec), type = types.DECISION_MESSAGE, flush=True)

        elif mxmsg.type == types.P300_ANALYSIS_RESULTS:
            res = variables_pb2.Sample()
            res.ParseFromString(mxmsg.message)
            LOGGER.debug("GOT P300 ANALYSIS RESULTS: "+str(res.channels))
            
            print "pdf_p300: ", res.channels
            self.pdf_p300 = np.array( res.channels )


            # Probabilty from etr
            pdf_etr = self.pdf_etr            
            
            # Probability from p300
            pdf_p300 = self.pdf_p300
            
            # Hybryd probability
            pdf = 0.5*(pdf_etr + pdf_p300)

            # Debugging leftouts...
            LOGGER.debug("pdf_etr: " +str(pdf_etr))
            LOGGER.debug("pdf_p300: " +str(pdf_p300))
            LOGGER.debug("pdf: " + str(pdf))
                        
            dec = -1
            
            # If both interfaces return significant value
            if (pdf>self.thresholdPercent).sum() == 1:
                dec = int(np.arange(self.cols*self.rows)[pdf==pdf.max()])
                LOGGER.info("Dec: " + str(dec))
            
            # If only P300 declares significant and all ETR values are highly insignificant
            elif ((pdf_p300>self.p300Tr).sum() == 1) and (pdf_etr<self.etrTr).all():
                dec = int(np.arange(self.cols*self.rows)[pdf_p300==pdf_p300.max()])
                LOGGER.info("Dec (only p300): " + str(dec))

            # If only ETR declares significant and all P300 values are highly insignificant
            elif (pdf_p300<self.p300Tr).all() and ((pdf_etr>self.etrTr).sum() == 1):
                dec = int(np.arange(self.cols*self.rows)[pdf_etr==pdf_etr.max()])
                LOGGER.info("Dec (only etr): " + str(dec))

            # If decision is to be made
            if dec != -1:
                self.conn.send_message(message = str(dec), type = types.DECISION_MESSAGE, flush=True)
                
        self.no_response()

if __name__ == "__main__":
    P300EtrDecision(settings.MULTIPLEXER_ADDRESSES).loop()
