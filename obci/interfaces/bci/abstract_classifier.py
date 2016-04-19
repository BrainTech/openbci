#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc, copy


class AbstractClassifier:
    """Base class for all classifiers."""
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def classify(self, chunk):
        """Compute set of classification probabilities for a given chunk of data.

        Args:
            chunk: numpy 2D data array (channels × samples)

        Returns:
            dict. dictionary of {target: probability},
            or None if classification could not be performed
        """
        pass

    def clone(self):
        """Return an independent copy of this classifier.
        Can be overriden to implement more efficient cloning,

        Returns:
            AbstractClassifier. copy of this classifier
        """
        return copy.copy(self)

    @abc.abstractmethod
    def learn(self, chunk, target):
        """Learn that given chunk of data represents given target.

        Args:
            chunk: numpy 2D data array (channels × samples)
            target: name of the target
        """
        pass
