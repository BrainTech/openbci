#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc, os, pickle
from threading import Thread
from Queue import Queue

from multiplexer.multiplexer_constants import peers, types
from obci.control.peer.configured_multiplexer_server import ConfiguredMultiplexerServer
from obci.configs import variables_pb2
from obci.utils.openbci_logging import log_crash


class AnalysisMaster(ConfiguredMultiplexerServer):
    """Base class for all peers implementing BCI
    (can be used for both calibration and decision phase)."""
    __metaclass__ = abc.ABCMeta

    # ----------------
    # abstract methods
    # ----------------

    @abc.abstractmethod
    def add_result(self, blink, probabilities):
        """This method is called whenever a classification result, consisting of
        a single blink and classification probabilities, is available.
        The implementation may simply send decision message based on the highest
        probability, or perform some advanced result post-processing.

        Needs to be implemented in subclass.

        Args:
            blink: information contained in a single blink
            probabilities (dict): dictionary of {target: probability}
        """
        pass

    @abc.abstractmethod
    def create_buffer(self, channel_count, ret_func):
        """Create an empty buffer with given return function.
        Needs to be implemented in subclass.

        Args:
            channel_count (int): number of channels in the input signal
            ret_func: function which should be passed to a buffer as "ret_func"

        Returns:
            buffer instance
        """
        return None

    @abc.abstractmethod
    def create_classifier(self):
        """Create a classifier to be used.
        Needs to be implemented in subclass.

        Returns:
            AbstractClassifier. classifier instance
        """
        return None

    @abc.abstractmethod
    def identify_blink(self, blink):
        """Identify to which target the given blink belongs, based on
        some external (e.g. GUI) information. If this information
        is not available (outside calibration phase), return None.
        This method is NOT meant to use machine learning techniques.

        Needs to be implemented in subclass.
        This method will be run by a separate thread.

        Args:
            blink: information contained in a single blink

        Returns:
            string. name of the target
            or None if identification could not be performed
        """
        return None

    @abc.abstractmethod
    def init_params(self):
        """Needs to be implemented in subclass."""
        pass

    # -------------------------------
    # optionally overridable methods
    # -------------------------------

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
        return classifier.classify(chunk)

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
        classifier.learn(chunk, target)

    # ----------------
    # internal methods
    # ----------------

    @log_crash
    def __init__(self, addresses, type=peers.ANALYSIS):
        super(AnalysisMaster, self).__init__(addresses=addresses, type=type)
        # initialize parameters of the subclass
        self.init_params()
        channel_count = len(self.config.get_param('channel_names').split(';'))
        self.buffer = self.create_buffer(channel_count, self._buffer_ret_func)

        # load classifier from file, if requested
        self.wisdom_path = self.config.get_param('wisdom_path') if self.config.has_param('wisdom_path') else None
        self._classifier = self._get_classifier()

        # array of requests to classification thread
        self.queue_classification = Queue()
        # array of requests to learning thread
        self.queue_learning = Queue()

        # separate thread for classification
        classification = Thread(target=self._run_classification)
        classification.daemon = True
        classification.start()

        # separate thread for learning
        learning = Thread(target=self._run_learning)
        learning.daemon = True
        learning.start()

        self.ready()

    def _buffer_ret_func(self, blink, chunk=None):
        """Internal function for the buffer object.

        Args:
            blink: information contained in a single blink
            chunk: numpy 2D data array (channels × samples)
        """
        if chunk is None:
            chunk = blink
            blink = None
        request = {'chunk': chunk, 'blink': blink}
        target = self.identify_blink(blink)
        if target is None:
            self.queue_classification.put(request)
        else:
            request['target'] = target
            self.queue_learning.put(request)

    def _get_classifier(self):
        """Provide a classifier object from file or create a new one.

        Returns:
            AbstractClassifier. a classifier object
        """
        if self.config.has_param('wisdom_load') and os.path.isfile(self.wisdom_path):
            with open(self.wisdom_path, 'rb') as wisdom_file:
                return pickle.load(wisdom_file)
        else:
            return self.create_classifier()

    def _run_classification(self):
        """This method will be run as a separate thread."""
        while True:
            request = self.queue_classification.get()
            probabilities = self.classify(self._classifier, request['chunk'], request['blink'])
            if probabilities is not None:
                self.add_result(request['blink'], probabilities)

    def _run_learning(self):
        """This method will be run as a separate thread."""
        while True:
            request = self.queue_learning.get()
            clone = self._classifier.clone()
            self.learn(clone, request['chunk'], request['target'])
            if self.wisdom_path is not None:
                with open(self.wisdom_path, 'wb') as wisdom_file:
                    pickle.dump(clone, wisdom_file)
            self._classifier = clone

    def handle_message(self, mxmsg):
        """Internal method, fired every time message is received.

        Args:
            mxmsg: message data
        """
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
            # we have received part of the signal
            data = variables_pb2.SampleVector()
            data.ParseFromString(mxmsg.message)
            self.buffer.handle_sample_vect(data)

        elif mxmsg.type == types.BLINK_MESSAGE:
            # we have received a single blink
            data = variables_pb2.Blink()
            data.ParseFromString(mxmsg.message)
            self.buffer.handle_blink(data)

        else:
            self.logger.warning("Got unrecognised message type: "+str(mxmsg.type))
        self.no_response()
