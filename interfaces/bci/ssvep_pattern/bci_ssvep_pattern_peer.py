#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#
from obci.interfaces.bci.ssvep_csp import bci_ssvep_csp_peer
from obci.interfaces.bci.ssvep_pattern import bci_ssvep_pattern_analysis
from obci.utils import context as ctx
from obci.configs import settings

class BCISsvepPattern(bci_ssvep_csp_peer.BCISsvepCsp):
    def _get_analysis(self, send_func, freqs, cfg, montage_matrix):
        """Fired in __init__ method.
        Return analysis instance object implementing interface:
        - get_requested_configs()
        - set_configs(configs)
        - analyse(data)
        """
        context = ctx.get_new_context()
        context['logger'] = self.logger
        return bci_ssvep_csp_analysis.BCISsvepPatternAnalysis(
            send_func,
            freqs,
            cfg,
            montage_matrix,
            self.config.get_param('channel_names').split(';'),
            self.config.get_param('channel_gains').split(';'),
            int(self.config.get_param('sampling_rate')),
            context)

    def _get_montage_matrix(self, cfg):
        return cfg['montage_matrix']


if __name__ == "__main__":
    BCISsvepPattern(settings.MULTIPLEXER_ADDRESSES).loop()
