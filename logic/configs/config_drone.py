#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Config(object):
    def __init__(self):
        self.number_of_decisions = 8
        self.number_of_states = 2
        self.states_configs = ['state', 'letters', 'actions',
                               'letters_solver', 'actions_solver']
        self.other_configs = []
        self.state = self.number_of_states * [self.number_of_decisions * [0]]
        self.state[0] = [1, 1, 1, 0, 0, 1, 0, 0]
        self.state[1] = [1, 1, 1, 1, 1, 1, 1, 0]
        self.letters = self.number_of_states * [self.number_of_decisions * [""]]
        self.letters[0] = [u"Start", u"Start",u"Start", u"",u"",u"Start", u"", u""]
        #self.letters[0] = [u"Lewo", u"Prosto",u"Prawo", u"",u"",u"Tył", u"", u""]
        self.letters[1] = [u"Lewo", u"Prosto",u"Prawo", u"",u"",u"Tył", u"", u""]
        self.letters_solver = self.number_of_states * [self.number_of_decisions * [""]]
        self.actions = self.number_of_states * [self.number_of_decisions * [""]]
        self.actions[0] = [u"robot('takeoff')" ,u"robot('takeoff')",  u"robot('takeoff')",u"", u"",u"robot('takeoff')",u"",u""]
        self.actions[1] = [u"robot('turn_left')" ,u"robot('forward')",  u"robot('turn_right')",u"", u"",u"robot('backward')",u"",u""]
        self.actions_solver = self.number_of_states * [self.number_of_decisions * [""]]
