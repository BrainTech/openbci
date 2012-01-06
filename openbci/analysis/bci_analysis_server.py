#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2, configurer

import random, time
import analysis_logging as logger

LOGGER = logger.get_logger("bci_analysis_server")

from openbci.online_analysis import auto_ring_buffer



class BCIAnalysisServer(BaseMultiplexerServer):
    def send_decision(self, dec):
        """Send dec message to the system (probably to LOGIC peer).
        dec is of integer type."""

        LOGGER.info("Sending dec message: "+str(dec))
        l_dec_msg = variables_pb2.Decision()
        l_dec_msg.decision = dec
        l_dec_msg.type = 0
        self.conn.send_message(message = l_dec_msg.SerializeToString(), type = types.DECISION_MESSAGE, flush=True)

    def __init__(self, addresses):
        #Create a helper object to get configuration from the system
        configurer_ = configurer.Configurer(addresses)
        
        #Create analysis object to analyse data 
        self.analysis = self._get_analysis(self.send_decision)

        requested_configs = self.get_requested_configs()
        LOGGER.info("Request system settings ...")
        configs = configurer_.get_configs(requested_configs)
        self.configs = configs
        LOGGER.info("Got system settings ...")

        #Set internal configuration for analysis
        self.analysis.set_configs(configs)

        #Initialise round buffer that will supply analysis with data
        #See auto_ring_buffer documentation
        sampling = int(configs['SamplingRate'])
        self.buffer = auto_ring_buffer.AutoRingBuffer(
            from_sample=int(float(configs['ANALYSIS_BUFFER_FROM'])*sampling),
            samples_count=int(float(configs['ANALYSIS_BUFFER_COUNT'])*sampling),
            every=int(float(configs['ANALYSIS_BUFFER_EVERY'])*sampling),
            num_of_channels=int(configs['NumOfChannels']),
            ret_func=self.analysis.analyse,
            ret_format=configs['ANALYSIS_BUFFER_RET_FORMAT'],
            copy_on_ret=int(configs['ANALYSIS_BUFFER_COPY_ON_RET'])
            )

        self.hold_after_dec = float(configs['ANALYSIS_HOLD_AFTER_DEC'])
        self._to_hold = 0.0

        super(BCIAnalysisServer, self).__init__(addresses=addresses, type=peers.ANALYSIS)

        #Send 'I am ready' message
        configurer_.set_configs({'PEER_READY':str(peers.ANALYSIS)}, self.conn)
        LOGGER.info("BCIAnalysisServer init finished!")

    def get_requested_configs(self):
        #Ask analysis for its internal required configs (to be set in hashtable)
        requested_configs = self.analysis.get_requested_configs()

        #Define which peers should we wait for
        #requested_configs.append('PEER_READY'+str(peers.UGM))
        #requested_configs.append('PEER_READY'+str(peers.LOGIC))
        requested_configs.append('PEER_READY'+str(peers.AMPLIFIER))

        #Add some other required configs
        requested_configs += ['NumOfChannels', 'SamplingRate', 
                              'ANALYSIS_BUFFER_FROM', 'ANALYSIS_BUFFER_COUNT', 'ANALYSIS_BUFFER_EVERY',
                              'ANALYSIS_BUFFER_RET_FORMAT', 'ANALYSIS_BUFFER_COPY_ON_RET','ANALYSIS_HOLD_AFTER_DEC']
        return requested_configs
        
    def handle_message(self, mxmsg):
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
	    l_msg = variables_pb2.SampleVector()
            l_msg.ParseFromString(mxmsg.message)
            #Supply buffer with sample data, the buffer will fire its
            #ret_func (that we defined as self.analysis.analyse) every 'every' samples
            self.buffer.handle_sample_vect(l_msg)
        self.no_response()

    def _get_analysis(self, send_func):
        """Fired in __init__ method.
        Return analysis instance object implementing interface:
        - get_requested_configs()
        - set_configs(configs)
        - analyse(data)
        """
        raise Exception("To be implemented!")
            
