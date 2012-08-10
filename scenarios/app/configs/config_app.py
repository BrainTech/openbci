#!/usr/bin/env python
# -*- coding: utf-8 -*-
from logic.configs import config_speller_8
from logic.configs import config_robot_8
class Config(object):
    def __init__(self):
        self.number_of_decisions = 8
        speller = config_speller_8.Config()
        robot = config_robot_8.Config()

        self.state = []
        self.actions = []
        self.letters = []

        #MENU
        menu_state = 0
        self.letters.append([u"Speller",u"Robot"
                             ,"Media", "", #u"High SSVEP",u"Low SSVEP"
                             u"", u"", u"", u"Back"])
        self.actions.append([
                "",
                "start_robot_feedback()", 
                "", 
                "", 
                "", "", "", "transform_scenario('main_menu')"])
        self.state.append([0]*self.number_of_decisions)
        self._setup_menu()
        zero_state = 1

        #SPELLER
        speller_state = zero_state
        for i, s in enumerate(speller.state):
            self.state.append([x+speller_state for x in s])
            self.actions.append(speller.actions[i])
            self.letters.append(speller.letters[i])
        self.state[zero_state][-1] = 0 #GOTO MENU
        self.actions[zero_state][-1] = "clear()"
        zero_state += len(speller.state)

        #ROBOT
        robot_state = zero_state
        for i, s in enumerate(robot.state):
            self.state.append([x+robot_state for x in s])
            self.actions.append(robot.actions[i])
            self.letters.append(robot.letters[i])
        self.state[zero_state][-1] = 0 #GOTO MENU
        self.actions[zero_state][-1] = "stop_robot_feedback()"
        zero_state += len(robot.state)


        self.state[menu_state][0] = speller_state
        self.state[menu_state][1] = robot_state


        self.number_of_states = zero_state
        self.states_configs = ['state', 'letters', 'actions', 'letters_solver', 'actions_solver']
        self.other_configs = []
        self.letters_solver = self.number_of_states * [self.number_of_decisions * [""]]
        self.actions_solver = self.number_of_states * [self.number_of_decisions * [""]]


    def _setup_menu(self):
        pass
