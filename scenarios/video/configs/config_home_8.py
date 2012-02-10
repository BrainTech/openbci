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
        self.state[0] = [0, 0, 0, 0, 0, 0, 0, 0]

        # Letters definition for every state. Normally for every state it should be a collection of strings.
        self.letters = self.number_of_states * [self.number_of_decisions * [""]]
        self.letters[0] = [
            [u"Lamp(OFF)", u"Lamp(ON)"],
            [u"Music(OFF)", u"Music(ON)"], 
            '',
            '', '', '', '', u'Finish']
        self.letters_solver = self.number_of_states * [self.number_of_decisions * [""]]
        self.letters_solver[0] = ['solve(0)', 'solve(1)', '', '',
                                  '', '', '', '']

        self.actions = self.number_of_states * [self.number_of_decisions * [""]]

        self.actions[0] = [
            ['run_ext(\'tahoe  "power on 1\\n\\r"\')', 'run_ext(\'tahoe  "power off 1\\n\\r"\')'], 
            ['run_ext(\'tahoe  "power on 2\\n\\r"\')', 'run_ext(\'tahoe  "power off 2\\n\\r"\')'], 
            '', 
            '', '', '', '', "finish("+self._finish_params()+")"]

        self.actions_solver = self.number_of_states * [self.number_of_decisions * [""]]
        self.actions_solver[0] = ['solve(0)', 'solve(1)', '', '',
                                  '', '', '', '']


    def _finish_params(self):
        return "x, x"
