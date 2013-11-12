#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:
#     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
#

import random, time, pickle

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer

from obci.configs import settings, variables_pb2
from obci.devices import appliance_helper
from obci.acquisition import acquisition_helper
from obci.gui.ugm import ugm_helper
from obci.analysis.buffers import auto_blink_buffer
from obci.interfaces.bci.p300_fda import bci_p300_fda_analysis
from obci.utils import context as ctx
from obci.utils import tags_helper
import csp_helper

from obci.utils import streaming_debug
from obci.utils.openbci_logging import log_crash

DEBUG = True

class BCIP300Fda(ConfiguredMultiplexerServer):
    def send_decision(self, dec):
        """Send dec message to the system (probably to LOGIC peer).
        dec is of integer type."""
        self.logger.info("Sending dec message: "+str(dec))
        self._last_dec_time = time.time()

        #self.buffer.clear() dont do it in p300 - just ignore some blinks sometimes ...
        self.buffer.clear_blinks()
        ugm_helper.send_stop_blinking(self.conn)
        self.conn.send_message(message = str(dec), type = types.DECISION_MESSAGE, flush=True)

        t = time.time()
        tags_helper.send_tag(
            self.conn, t, t, 
            "decision",
            {'decision':str(dec)})
        self.conn.send_message(message = str(self.blink_field_ids[dec]), type = types.DECISION_MESSAGE, flush=True)

    @log_crash
    def __init__(self, addresses):
        #Create a helper object to get configuration from the system
        super(BCIP300Fda, self).__init__(addresses=addresses,
                                          type=peers.P300_ANALYSIS)
        #get stats from file
        cfg = self._get_csp_config()
        cfg['pPercent'] = float(self.config.get_param('analysis_treshold'))
        cfg['nMin'] = int(self.config.get_param("n_min"))
        cfg['nMax'] = int(self.config.get_param("n_max"))
        cfg['nLast'] = int(self.config.get_param("n_last"))
        
        cfg['debug_flag'] = int(self.config.get_param('debug_flag'))
        
        montage_matrix = self._get_montage_matrix(cfg)
        blink_field_ids = self.config.get_param('blink_field_ids').split(';')
        self.blink_field_ids = [int(ids) for ids in blink_field_ids]
        

        #Create analysis object to analyse data 
        self.analysis = self._get_analysis(self.send_decision, cfg, montage_matrix)

        #Initialise round buffer that will supply analysis with data
        #See auto_ring_buffer documentation
        sampling = int(self.config.get_param('sampling_rate'))
        channels_count = len(self.config.get_param('channel_names').split(';'))
        self.buffer = auto_blink_buffer.AutoBlinkBuffer(
            from_blink=0,
            samples_count=int(float(cfg['buffer'])),
            sampling=sampling,
            num_of_channels=channels_count,
            ret_func=self.analysis.analyse,
            ret_format=self.config.get_param('buffer_ret_format'),
            copy_on_ret=int(self.config.get_param('buffer_copy_on_ret'))
            )
        
        self.hold_after_dec = float(self.config.get_param('hold_after_dec'))
        if DEBUG:
            self.debug = streaming_debug.Debug(int(self.config.get_param('sampling_rate')),
                                               self.logger,
                                               int(self.config.get_param('samples_per_packet')))
                                                   
        self._last_dec_time = time.time() + 1 #sleep 5 first seconds..
        ugm_helper.send_start_blinking(self.conn)
        self.ready()
        self.logger.info("BCIAnalysisServer init finished!")

    def handle_message(self, mxmsg):
        #always buffer signal
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
            l_msg = variables_pb2.SampleVector()
            l_msg.ParseFromString(mxmsg.message)
            #Supply buffer with sample data, the buffer will fire its
            #ret_func (that we defined as self.analysis.analyse) every 'every' samples
            self.buffer.handle_sample_vect(l_msg)
            if DEBUG:
                self.debug.next_sample()

        #process blinks only when hold_time passed
        if self._last_dec_time > 0:
            t = time.time() - self._last_dec_time
            if t > self.hold_after_dec:
                self._last_dec_time = 0
                ugm_helper.send_start_blinking(self.conn)
            else:
                self.no_response()
                return

        if mxmsg.type == types.BLINK_MESSAGE:
            l_msg = variables_pb2.Blink()
            l_msg.ParseFromString(mxmsg.message)
            self.buffer.handle_blink(l_msg)
            
        self.no_response()

    def _get_analysis(self, send_func, cfg, montage_matrix):
        """Fired in __init__ method.
        Return analysis instance object implementing interface:
        - get_requested_configs()
        - set_configs(configs)
        - analyse(data)
        """
        context = ctx.get_new_context()
        context['logger'] = self.logger
        return bci_p300_fda_analysis.BCIP300FdaAnalysis(
            send_func,
            cfg,
            montage_matrix,
            int(self.config.get_param('sampling_rate')),
            int(self.config.get_param('dec_count')),
            context)


    def _get_csp_config(self):
        return csp_helper.get_csp_config(
            self.config.get_param('config_file_path'),
            self.config.get_param('config_file_name'))

    def _get_montage_matrix(self, cfg):
        return csp_helper.get_montage_matrix(
            self.config.get_param('channel_names').split(';'),
            cfg['use_channels'].split(';'),
            cfg['montage'],
            cfg['montage_channels'].split(';'))
        

if __name__ == "__main__":
    BCIP300Fda(settings.MULTIPLEXER_ADDRESSES).loop()
