#!/usr/bin/env python
# -*- coding: utf-8 -*-
from multiplexer.multiplexer_constants import peers, types
import settings, variables_pb2, configurer
import csp_bci_analysis
from analysis import bci_analysis_server

class CspBCIAnalysisServer(bci_analysis_server.BCIAnalysisServer):
    def _get_analysis(self, send_func):
        """Fired in __init__ method.
        Return analysis instance object implementing interface:
        - get_requested_configs()
        - set_configs(configs)
        - analyse(data)
        """
        return csp_bci_analysis.CspBCIAnalysis(send_func)

if __name__ == "__main__":
    CspBCIAnalysisServer(settings.MULTIPLEXER_ADDRESSES).loop()
