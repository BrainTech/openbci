#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Config(object):
    def __init__(self):
        self.number_of_decisions = 8
        self.number_of_states = 1
        self.states_configs = ['state', 'letters', 'actions',
                               'letters_solver', 'actions_solver']
        self.other_configs = []
        self.state = self.number_of_states * [self.number_of_decisions * [0]]
        self.state[0] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.letters = self.number_of_states * [self.number_of_decisions * [""]]
        self.letters[0] = [u"Turn Left",u"Left", u"Fwd",u"Right", u"Turn right",u"Land",u"Take off", u"reset"]
        self.letters_solver = self.number_of_states * [self.number_of_decisions
                                                       * [""]]
        self.actions = self.number_of_states * [self.number_of_decisions * [""]]
        self.actions[0] = [u"robot('turn_left')" ,u"robot('left')",  u"robot('forward')",u"robot('right')",
                           u"robot('turn_right')",u"robot('land')",u"robot('takeoff')",u"robot('reset')"]
        self.actions_solver = self.number_of_states * [self.number_of_decisions
                                                       * [""]]
        def _finish_action(self):
            return "finish()"
