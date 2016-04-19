#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from obci.interfaces.bci.abstract_classifier import AbstractClassifier


class DummyClassifier(AbstractClassifier):

    def classify(self, chunk):
        print("classify called with chunk shaped "+str(chunk.shape))
        return {'thetarget': 1.0}

    def learn(self, chunk, target):
        print("learn ("+target+") called with chunk shaped "+str(chunk.shape))
