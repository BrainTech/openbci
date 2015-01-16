#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os.path, time
from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import settings, variables_pb2
from obci.exps.ventures import analysis_stable
from obci.exps.ventures.data import data_manager
from obci.acquisition import acquisition_helper


class LogicVenturesStable(ConfiguredMultiplexerServer):
    def __init__(self, addresses):
        super(LogicVenturesStable, self).__init__(addresses=addresses,
                                                type=peers.CLIENT)
        self.ready()
        user_id = self.get_param('user_id')
        file_name = self.get_param('file_name')
        file_path = self.get_param('file_path')
        self.logger.info("start waiting for saving finished")
        acquisition_helper.wait_saving_finished(addresses, ['wii'])

        self.logger.info("saving finished! Start analysis for: "+user_id+" , to file_path: "+file_path+" and file_name: "+file_name)
        xa,ya,xb,yb,xc,yc = analysis_stable.calculate(file_path, file_name)
        self.logger.info('Baseline calculated: '+','.join([repr(xa), repr(ya), repr(xb), repr(yb), repr(xc), repr(yc)]))

        data_manager.baseline_set(user_id, xa, ya, xb, yb, xc, yc, file_name)
        self.logger.info('Baseline data properly stored!')
        sys.exit(0)
    
if __name__ == "__main__":
    LogicVenturesStable(settings.MULTIPLEXER_ADDRESSES).loop()
