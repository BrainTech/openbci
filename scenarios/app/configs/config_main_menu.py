#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Config(object):
    def __init__(self):
        self.number_of_decisions = 8
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
        self.state = self.number_of_states * [self.number_of_decisions * [0]]

       # Letters definition for every state. Normally for every state it should be a collection of strings.
        self.letters = self.number_of_states * [self.number_of_decisions * [""]]
        self.letters[0] = [u"Switch",u"P300",u"SSVEP",u"",
                           u"", u"   P300  \ncalibrate", u" SSVEP  \ncalibrate", u"SSVEP buf\ncalibrate"]
        self.letters_solver = self.number_of_states * [self.number_of_decisions * [""]]
        
        # thanks to corresponding values from actions_solver obci will decide which program to use.
        self.actions = self.number_of_states * [self.number_of_decisions * [""]]
        self.actions[0] = ["transform_scenario('switch')", 
                           "transform_scenario('p300')",
                           "transform_scenario('ssvep')",
                           "",
                           "",
                           "transform_scenario('p300_calib')",
                           "transform_scenario('ssvep_calib')",
                           "transform_scenario('ssvep_buff_calib')",
                           ]

        self.actions_solver = self.number_of_states * [self.number_of_decisions * [""]]
