#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# OpenBCI - framework for Brain-Computer Interfaces based on EEG signal
# Project was initiated by Magdalena Michalska and Krzysztof Kulewski
# as part of their MSc theses at the University of Warsaw.
# Copyright (C) 2008-2009 Krzysztof Kulewski and Magdalena Michalska
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#      Marian Dovgialo <marian.dowgialo@gmail.com>

from obci.configs import settings
from multiplexer.multiplexer_constants import peers, types
from obci.interfaces.bci.analysis_master import AnalysisMaster
from obci.interfaces.bci.p300_MD.p300_classm import P300EasyClassifier
from obci.interfaces.bci.p300_MD.p300_classm import _feature_extraction_singular

from obci.interfaces.bci.p300_MD.helper_functions import get_montage, get_montage_matrix_custom
from obci.interfaces.bci.p300_MD.helper_functions import leave_channels_array, get_channel_indexes

from obci.analysis.buffers.auto_blink_buffer import AutoBlinkBuffer
from collections import defaultdict, deque
from operator import itemgetter
from obci.utils.openbci_logging import log_crash
import sys
from obci.interfaces.bci.p300_MD.helper_functions import get_epochs_fromfile
from obci.interfaces.bci.p300_MD.helper_functions import evoked_pair_plot_smart_tags
import numpy as np
import os.path
import pickle
import pylab as pb
from obci.gui.ugm import ugm_helper

class P300MasterPeer(AnalysisMaster):
    '''P300 classifier master peer'''
    @log_crash
    def __init__(self, addresses):
        super(P300MasterPeer, self).__init__(addresses=addresses,
                                                type=peers.P300_ANALYSIS)
        
    
    def _reset_buffors(self):
        #probabilities of selected input for single epochs
        self.singular_proba_buffor = defaultdict(list)
        #probabilities of selected input for cumulative mean
        self.averaged_proba_buffor = defaultdict(list)
        #features buffor to classify on single epochs or cumulative mean
        self.features = defaultdict(list)
        #final decision buffor
        self.decision_buffor = deque(maxlen = self.decision_stop)
    
    def _prepare_chunk(self, chunk):
        '''
        Performs channel selection, montage and feature extraction.
        
        First Montage - look out for average montage and technical channels!!
        then channel selection
        then feature extraction
        
        Args:
            chunk: numpy 2D data array (channels × samples)
        '''
        
        chunk_montage = get_montage(
                                    chunk,
                                    self.montage_matrix
                                    )
        chunk_clean_channels, _ = leave_channels_array(
                                      chunk_montage,
                                      self.channels_for_classification,
                                      self.channel_names
                                      )
                                      
        
        chunk_ready = _feature_extraction_singular( 
                                        chunk_clean_channels,
                                        self.sampling_rate,
                                        self.baseline,
                                        self.window,
                                        self.targetFs,
                                        )
        return chunk_ready
    def _send_decision(self, decision):
        self.conn.send_message(message = str(decision), type = types.DECISION_MESSAGE, flush=True)
        self._reset_buffors()
    
    def add_result(self, blink, probabilities):
        '''
        Sends decision if some last decisions from cumulative mean
        are the same or a lot of averaging was done
        Args:
            blink: information contained in a single blink
            probabilities (dict): dictionary of {target: probability}
        '''
        #planning for future
        if probabilities:
            self.singular_proba_buffor[blink.index].append(
                                                probabilities['targetSingle']
                                                            )
            self.averaged_proba_buffor[blink.index].append(
                                                probabilities['targetCMean']
                                                            )
            last_single = [blink.index, probabilities['targetSingle']]
            last_mean = [blink.index, probabilities['targetCMean']]
            self.logger.info('Last single dec: {}, proba: {:.2f}'.format(
                                                                last_single[0],
                                                                last_single[1]))
            self.logger.info('Last mean dec: {}, proba: {:.2f}'.format(
                                                                last_mean[0],
                                                                last_mean[1]))
            if last_mean[1]>self.desision_stop_proba_thr:
                self.decision_buffor.append(blink.index)
            
            # enough of the same decisions condition
            one_decision = (len(set(self.decision_buffor)) == 1)
            buffor_full = (len(self.decision_buffor) == self.decision_stop)
            if one_decision and buffor_full:
                decision = self.decision_buffor[-1]
                self.logger.info('Decision by decision_stop {}'.format(decision))
                self._send_decision(decision)
                return
                
            # number of averaged epochs condition
            # ensure all buttons have been averaged self.maximum_to_average number of time
            minimum_averaged = min(
                len(self.averaged_proba_buffor[i]) for i in self.averaged_proba_buffor.keys()
                                )
            if minimum_averaged > self.maximum_to_average:
                most_confident_decision = max(
                                        self.averaged_proba_buffor.items(),
                                        key = lambda key: key[1][-1]
                                        )[0]
                self.logger.info('Decision by max_avr {}'.format(most_confident_decision))
                self._send_decision(most_confident_decision)
                return
            
        
    
    def create_buffer(self, channel_count, ret_func):
        
        return AutoBlinkBuffer(
            from_blink=int(self.sampling_rate*self.baseline),
            samples_count=int((self.window-self.baseline)*self.sampling_rate),
            sampling=self.sampling_rate,
            num_of_channels=channel_count,
            ret_func=ret_func,
            ret_format="NUMPY_CHANNELS",
            copy_on_ret=0
            )
            
    def create_classifier(self):
        try:
            with open(self.wisdom_path) as clf_file:
                classifier = pickle.load(clf_file)
            self.logger.info('loaded classifier from wisdom_path')
        except Exception as e:
            classifier = P300EasyClassifier(targetFs=self.targetFs)
            self.logger.info("Loading classifier failed: {}".format(e))
            self.logger.info('Creating new, untrained classifier')
        return classifier
    def identify_blink(self, blink):
        if self.training_index is not None:
            if blink.index == self.training_index:
                return 'target'
            else:
                return 'nontarget'
        return None
        
    @log_crash
    def init_params(self):
        self.logger.info('Initialasing parameters')
        #configdence (probability) level for internal decision to be counted to decision stop:
        self.desision_stop_proba_thr = self.config.get_param(
                                        'decision_stop_threshold').split(';')
        #available channels
        self.channel_names = self.config.get_param(
                                        'channel_names').split(';')
        #used channels 
        self.channels_for_classification = self.config.get_param(
                                        'channels_for_classification'
                                                        ).split(';')
        self.sampling_rate = float(
                                self.config.get_param('sampling_rate')
                                  )
        #channel montage:
        #montage type
        self.montage = 'custom'
        #montage channels
        channels_count = len(self.channel_names)
        self.montage_channels = self.config.get_param("montage_channels").strip().split(';')
        montage_ids = get_channel_indexes(self.channel_names, self.montage_channels)
        self.montage_matrix = get_montage_matrix_custom(channels_count,
                                                        montage_ids,
                                                        )
        
        #pre event baseline in seconds (negative) seconds
        self.baseline = float(
                                self.config.get_param('baseline')
                                  )
        #post event window to consider seconds
        self.window = float(
                                self.config.get_param('window')
                                  )
        
        #maximum averaged epochs
        #can be inf
        self.maximum_to_average = float(
                            self.config.get_param('maximum_to_average')
                                     )
        #identical decisions to get final answer
        self.decision_stop = int(self.config.get_param('decision_stop'))
        # downsample to
        self.targetFs = float(self.config.get_param('downsample_to'))
        # how many virtual "buttons"
        # in calibration session logic or something should set 
        # this parameter to show which field is being used for calibration
        try:
            self.training_index = int(
                                    self.config.get_param(
                                        'calibration_field_index')
                                 )
        except ValueError:
            self.training_index = None
                
        self.ignored_blink_ids = [int(i) for i in self.config.get_param('ignored_blink_ids').strip().split(';')]

        self.logger.info('Initialasing buffers')
        self._reset_buffors()
        self.ready()

        if self.config.get_param('offline_learning') == '1':
            self.logger.info('STARTING ONLINE LEARNING')
            self.learn_offline()
            self.logger.info('DONE LEARNING')
            sys.exit(0)
        
        
    @log_crash
    def learn_offline(self):
        '''Function that reads saved calibration signal, splits it
        to epochs and trains classifier'''
        self.logger.info("STARTING LEARNING")
        
        
        filter = None
        baseline = self.baseline
        window = self.window
        montage = [self.montage,]
        chnls = self.montage_channels
        self.logger.info("reference channels {}".format(chnls))
        montage = montage+chnls
        #dataset
        ds_path = self.config.get_param('offline_learning_dataset_path')
        ds_path = os.path.expanduser(ds_path)
            
            
        exclude_channels = exclude = list(
                                            set(self.channel_names
                                          ).difference(
                                            set(
                                                self.channels_for_classification
                                                )
                                            )
                                        )
        
        ept, epnt = get_epochs_fromfile(ds_path, filter = filter, duration = self.window+1,
                                    montage = montage,
                                    start_offset = baseline,
                                    drop_chnls = exclude_channels
                                    )
        self.logger.info("GOT {} TARGET EPOCHS AND {} NONTARGET".format(len(ept), len(epnt)))
        
        self.logger.info('EPOCH PARAMS:\n{}'.format(ept[0].get_params()))
        evoked_pair_plot_smart_tags(ept, epnt, labels=['target', 'nontarget'], chnames=['O1', 'O2'])
        self.wisdom_path = self.wisdom_path = self.config.get_param('wisdom_path')
        cl = P300EasyClassifier(targetFs=self.targetFs)
        result = cl.calibrate(ept, epnt, bas=baseline, window=window)
        
        self.logger.info('classifier self score on training set: {}'.format(result))
        with open(self.wisdom_path, 'w') as fname:
            pickle.dump(cl, fname)
        self.logger.info("classifier -- DONE")
        #plot features:
        f = np.array(cl.learning_buffor_features)
        l = np.array(cl.learning_buffor_classes)
        pb.plot(np.median(f[l==0], axis=0))
        pb.plot(np.median(f[l==1], axis=0))
        pb.show()
    
    
    def classify(self, classifier, chunk, blink):
        """Compute set of classification probabilities for a given blink.

        May be re-implemented in subclass to perform some pre-processing
        or feature extraction on the signal (chunk).
        This method will be run by a separate thread.

        Args:
            classifier (AbstractClassifier): classifier instance to be used for classification
            chunk: numpy 2D data array (channels × samples)
            blink: information contained in a single blink

        Returns:
            dict. dictionary of {target: probability},
            or None if classification could not be performed
            
        """
        if blink.index in self.ignored_blink_ids:
            return None
        chunk_ready = self._prepare_chunk(chunk)
        self.features[blink.index].append(chunk_ready)
        probabilities = {}
        probabilities['targetSingle'] = classifier.classify(
                                                            chunk_ready
                                                                    )
        chunk_mean = np.array(self.features[blink.index]).mean(axis=0)
        probabilities['targetCMean'] = classifier.classify(
                                                              chunk_mean
                                                                    )
        return probabilities
        
    def learn(self, classifier, chunk, target):
        """Learn that given chunk represents given target.

        May be re-implemented in subclass to perform some pre-processing
        or feature extraction on the signal (chunk).
        This method will be run by a separate thread.

        Args:
            classifier (AbstractClassifier): classifier instance to be used for learning
            chunk: numpy 2D data array (channels × samples)
            target: name of the target
        """
        chunk_ready = self._prepare_chunk(chunk)
        classifier.learn(chunk_ready, target)
        
if __name__ == '__main__':
    P300MasterPeer(settings.MULTIPLEXER_ADDRESSES).loop()
