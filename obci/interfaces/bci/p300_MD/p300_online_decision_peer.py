#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
from multiplexer.multiplexer_constants import peers, types
from obci.configs import settings, variables_pb2

from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.analysis.buffers import auto_blink_buffer
from obci.gui.ugm import ugm_helper
from obci.utils.openbci_logging import log_crash
from sklearn.externals import joblib
import os.path
from helper_functions import get_montage, get_montage_matrix_custom, get_channel_indexes
from p300_class import P300MetaClassifier

MAX_AVR = 1000
DECISION_STOP = 3
TARGETFS = 24
FEATURE_REDUCTION = None

class P300AnalysisPeer(ConfiguredMultiplexerServer):
    @log_crash
    def __init__(self, addresses):
        #Create a helper object to get configuration from the system
        super(P300AnalysisPeer, self).__init__(addresses=addresses,
                                          type=peers.P300_ANALYSIS)
        self.clf_filepath = os.path.join(
                                self.config.get_param('data_file_path'),
                                self.config.get_param('cl_filename'),
                                )
        blink_field_ids = self.config.get_param('blink_field_ids').split(';')
        self.blink_field_ids = [int(ids) for ids in blink_field_ids]
        sampling = int(self.config.get_param('sampling_rate'))
        self.sampling = sampling
        self.channel_names = self.config.get_param('channel_names').split(';')
        channels_count = len(self.channel_names)
        
        window = 0.6
        baseline = -.2
        self.buffer = auto_blink_buffer.AutoBlinkBuffer(
            from_blink=int(sampling*baseline),
            samples_count=int(window*sampling),
            sampling=sampling,
            num_of_channels=channels_count,
            ret_func=self.return_blink,
            ret_format="NUMPY_CHANNELS",
            copy_on_ret=0
            )
            
        self.clf = P300MetaClassifier(self.clf_filepath, MAX_AVR,
                        DECISION_STOP, TARGETFS, None, FEATURE_REDUCTION,
                        len(self.blink_field_ids))
                        
        
        
        self.montage = [self.config.get_param("montage")]
        self.montage_channels = self.config.get_param("montage_channels").strip().split(';')
        montage_ids = get_channel_indexes(self.channel_names, montage_channels)
        self.montage_matrix = get_montage_matrix_custom(channels_count,
                                                        montage_ids,
                                                        )
        ugm_helper.send_start_blinking(self.conn)
        self.ready()
    def return_blink(self, blink, data):
        '''function run after getting blink for a "button" highlight
        runs classifier for that button, if classifier says it's a target
        sends a message with decision
        (implies that classifier is sure about blink being a target)'''
        ind = blink.index
        self.logger.info('got blink index:{}\ndata:{}'.format(ind, data))
        
        data_ready = get_montage(data, self.montage_matrix)
        
        dec = self.clf.run(data_ready, self.sampling, self.blink_field_ids.index(ind)) #returns button ID
        self.buffer.clear_blinks() # buffor is used to get one blink, classifiers have their own
        if dec:
            ugm_helper.send_stop_blinking(self.conn)
            self.conn.send_message(message = str(self.blink_field_ids[ind]), type = types.DECISION_MESSAGE, flush=True)
            
    def handle_message(self, mxmsg):
        'sends signal to autoblinkbuffor'''
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
            l_msg = variables_pb2.SampleVector()
            l_msg.ParseFromString(mxmsg.message)
            self.buffer.handle_sample_vect(l_msg)
        if mxmsg.type == types.BLINK_MESSAGE:
            l_msg = variables_pb2.Blink()
            l_msg.ParseFromString(mxmsg.message)
            self.buffer.handle_blink(l_msg)
        self.no_response()
if __name__ == "__main__":
    P300AnalysisPeer(settings.MULTIPLEXER_ADDRESSES).loop()
