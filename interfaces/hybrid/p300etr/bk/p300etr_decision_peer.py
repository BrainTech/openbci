#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from obci_control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from configs import settings, variables_pb2
import random, time, sys
import numpy as np

from interfaces import interfaces_logging as logger

LOGGER = logger.get_logger("p300_etr_decision", "debug")


class P300EtrDecision(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(P300EtrDecision, self).__init__(addresses=addresses,
                                     type=peers.RESULTS_ANALYSIS)
        self.ready()

    def initConst(self):
        
        self.fields = 8
        self.tresholdValue = 0.95
        

    def handle_message(self, mxmsg):
        LOGGER.info("P300EtrDecision\n")
        if mxmsg.type == types.ETR_ANALYSIS_RESULTS:
            res = variables_pb2.Sample()
            res.ParseFromString(mxmsg.message)
            LOGGER.debug("GOT ETR ANALYSIS RESULTS: "+str(res.channels))

            #self.conn.send_message(message = str(dec), type = types.DECISION_MESSAGE, flush=True)
        elif mxmsg.type == types.P300_ANALYSIS_RESULTS:
            res = variables_pb2.Sample()
            res.ParseFromString(mxmsg.message)
            LOGGER.debug("GOT P300 ANALYSIS RESULTS: "+str(res.channels))

            #self.conn.send_message(message = str(dec), type = types.DECISION_MESSAGE, flush=True)

        # Probabilty from etr
        pdf_etr = np.random.random(8)
        
        # Probability from p300
        pdf_p300 = np.random.random(8)
        
        # Hybryd probability
        pdf = pdf_p300*pdf_etr
        
        # Assume pdf is T distribution
        loc = pdf.mean()
        scale = pdf.std()
        cdf = st.t.cdf(pdf, len(pdf), loc=loc, scale=scale)
        
        # If only one value is over threshold
        if np.sum( cdf > self.tresholdValue ) == 1:
            dec = int(np.arange(len(cdf))[cdf > self.tresholdValue])
            SEND_DECISION( dec )
            
        self.no_response

if __name__ == "__main__":
    P300EtrDecision(settings.MULTIPLEXER_ADDRESSES).loop()
