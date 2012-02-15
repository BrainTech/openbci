#!/usr/bin/env python
# -*- coding: utf-8 -*-

from launcher.launcher_tools import obci_root
import os.path

class Config(object):
    def __init__(self):
        self.number_of_decisions = 8
        self.number_of_states = 1

        # A list of all configs defined for every single state.
        self.states_configs = ['state', 'letters', 'actions', 'letters_solver', 'actions_solver']

        # A list of all configs defined as globals,
        # not assigned to any particular state.
        self.other_configs = []
        tahoe_path = os.path.join(obci_root(), 'devices', 'tahoe_http.py')

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
            [u"Lamp(off)", u"Lampa(on)"],
            [u"Muzyka(off)", u"Muzyka(on)"],
            '', '',
            '', '', '', u'Koniec']
        self.letters_solver = self.number_of_states * [self.number_of_decisions * [""]]
        self.letters_solver[0] = [
            'solve(0)', 'solve(1)',
            '', '',
            '', '', '', '']

        self.actions = self.number_of_states * [self.number_of_decisions * [""]]

        self.actions[0] = [
            ['run_ext(\''+tahoe_path+'  on 1\')', 'run_ext(\''+tahoe_path+'  off 1\')'],
            ['run_ext(\''+tahoe_path+'  on 2\')', 'run_ext(\''+tahoe_path+'  off 2\')'],
            '', '',
            '', '', '', "finish("+self._finish_params()+")"]

        self.actions_solver = self.number_of_states * [self.number_of_decisions * [""]]
        self.actions_solver[0] = [
            'solve(0)', 'solve(1)',
            '', '',
            '', '', '', '']


    def _finish_params(self):
        return "x, x"
