#!/usr/bin/env python
# -*- coding: utf-8 -*-
import settings
import sample_bci_analysis
import bci_analysis_server
class SampleBCIAnalysisServer(bci_analysis_server.BCIAnalysisServer):
    def _get_analysis(self, send_func):
        """Fired in __init__ method.
        Return analysis instance object implementing interface:
        - get_requested_configs()
        - set_configs(configs)
        - analyse(data)
        """
        return sample_bci_analysis.SampleBCIAnalysis(send_func)

if __name__ == "__main__":
    SampleBCIAnalysisServer(settings.MULTIPLEXER_ADDRESSES).loop()
