#!/usr/bin/env python
# -*- coding: utf-8 -*-
import settings
import ssvep_bci_analysis
import bci_analysis_server
class SsvepBCIAnalysisServer(bci_analysis_server.BCIAnalysisServer):
    def _get_analysis(self, send_func):
        """Fired in __init__ method.
        Return analysis instance object implementing interface:
        - get_requested_configs()
        - set_configs(configs)
        - analyse(data)
        """
        return ssvep_bci_analysis.SsvepBCIAnalysis(send_func)

if __name__ == "__main__":
    SsvepBCIAnalysisServer(settings.MULTIPLEXER_ADDRESSES).loop()
