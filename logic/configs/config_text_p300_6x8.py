#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# Author:
# Dawid Laszuk <laszukdawid@gmail.com>

import os

class Config(object):

    def __init__(self):
        self.number_of_decisions = 48
        self.number_of_states = 1

        # A list of all configs defined for every single state.
        self.states_configs = ['state', 'letters', 'actions', 'letters_solver', 'actions_solver']

        # A list of all configs defined as globals,
        # not assigned to any particular state.
        self.other_configs = []

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # !!! Only keys defined in states_configs and other_configs 
        # will be visible in your application.!!!
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # States transition matrix
        self.state = [self.number_of_decisions * [0]]

        # Graphics definition for every state. Normally for every state it should be a collection of strings.
        # Hovewever, sometimes we have a collection of strings, not a single string. It happens when we have a 'dynamic' state.
        # In that case there should be a corresponding graphics_solver variable with method that resolves graphics definition at runtime.
        self.letters =  [['A', 'B', 'C', 'D', 'E', 'F', '1', '2', 
                          'G', 'H', 'I', 'J', 'K', 'L', '3', '4', 
                          'M', 'N', 'O', 'P', 'Q', 'R', '5', '6', 
                          'S', 'T', 'U', 'V', 'W', 'X', '7', '8', 
                          'Y', 'Z', '_', '?', 'comma', 'dot','9', '0', 
                          '<', '<<', 'clear', 'retrieve','send', 'call', 'say', 'help']]


        # See descripton above.
        self.letters_solver = [[""]*self.number_of_decisions]

        # Import text
        with open(os.path.expanduser(r"~/text_to_display")) as f:
             text = [t.strip() for t in f.readlines()]
        
        while( len(text) < self.number_of_decisions):
            text.append("koniec...")
            
        self.actions = ["msg('%s')"%text[index] for index in range(self.number_of_decisions)]
        self.actions = [u'mult_action(["clear()", "%s"])'%action for action in self.actions]
        self.actions = [self.actions]


        # See description above.
        self.actions_solver = [[""]*self.number_of_decisions]

    def _finish_action(self):
        return "finish()"
