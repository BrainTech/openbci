#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
from multiplexer.multiplexer_constants import peers, types
from obci.configs import settings
from obci.interfaces.bci.analysis_master import AnalysisMaster
from obci.interfaces.bci.budzik.experimental.dummy_classifier import DummyClassifier
from obci.analysis.buffers.auto_blink_buffer import AutoBlinkBuffer


class BudzikPrototype(AnalysisMaster):

    def __init__(self, addresses):
        super(BudzikPrototype, self).__init__(addresses=addresses, type=peers.P300_ANALYSIS)
        self.last_index = None

    def add_result(self, blink, probabilities):
        target = max(probabilities, key=probabilities.get)
        if target == 'thetarget':
            index = blink.index
            if index == self.last_index:
                self.conn.send_message(message=str(index), type=types.P300_DECISION_MESSAGE, flush=True)
            self.last_index = index
        else:
            self.last_index = None

    def create_buffer(self, channel_count, ret_func):
        sampling_rate = int(self.config.get_param('sampling_rate'))
        buffer_length = float(self.config.get_param('buffer_length'))
        buffer_length_samples = int(buffer_length * sampling_rate)
        return AutoBlinkBuffer(
            from_blink=buffer_length_samples,
            samples_count=buffer_length_samples,
            num_of_channels=channel_count,
            sampling=sampling_rate,
            ret_func=ret_func,
            ret_format='NUMPY_CHANNELS',
            copy_on_ret=False
        )

    def create_classifier(self):
        return DummyClassifier()

    def identify_blink(self, blink):
        # since we don't switch from learning to classification (yet)
        # let's randomly choose to learn or to classify
        if random.randint(2):
            return 'thetarget'
        else:
            return None

    def init_params(self):
        pass

if __name__ == "__main__":
    # initialize and run an object in order to have your peer up and running
    BudzikPrototype(settings.MULTIPLEXER_ADDRESSES).loop()
