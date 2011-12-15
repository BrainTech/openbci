#!/usr/bin/env python
# -*- coding: utf-8 -*-
from multiplexer.multiplexer_constants import peers, types
import settings, variables_pb2, configurer
import ssvep_bci_analysis
import bci_analysis_server
import analysis_logging as logger
LOGGER = logger.get_logger("ssvep_bci_analysis_server")

class SsvepBCIAnalysisServer(bci_analysis_server.BCIAnalysisServer):
    def __init__(self, addresses):
        super(SsvepBCIAnalysisServer, self).__init__(addresses)
        self.running = int(self.configs['SSVEP_RUNNING_ON_START'])

    def get_requested_configs(self):
        configs = super(SsvepBCIAnalysisServer, self).get_requested_configs()
        configs.append('SSVEP_RUNNING_ON_START')
        return configs

    def _get_analysis(self, send_func):
        """Fired in __init__ method.
        Return analysis instance object implementing interface:
        - get_requested_configs()
        - set_configs(configs)
        - analyse(data)
        """
        return ssvep_bci_analysis.SsvepBCIAnalysis(send_func)

    def handle_message(self, mxmsg):
        if mxmsg.type == types.SSVEP_CONTROL_MESSAGE:
	    l_msg = variables_pb2.Variable()
            l_msg.ParseFromString(mxmsg.message)
            if l_msg.key == 'stop':
                LOGGER.info("Stop ssvep!")
                self._stop()
            elif l_msg.key == 'start':
                LOGGER.info("Start ssvep!")
                self._start()
            else:
                LOGGER.warning("Unrecognised ssvep control message! "+str(l_msg.key))
        
        if self.running:
            super(SsvepBCIAnalysisServer, self).handle_message(mxmsg)
        else:
            self.no_response()
    
    def _stop(self):
        self.running = False
        self.buffer.clear()

    def _start(self):
        self.running = True

if __name__ == "__main__":
    SsvepBCIAnalysisServer(settings.MULTIPLEXER_ADDRESSES).loop()
