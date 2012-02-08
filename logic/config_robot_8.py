#!/usr/bin/env python
# -*- coding: utf-8 -*-

number_of_decisions = 8
number_of_states = 2

# A list of all configs defined for every single state.
states_configs = ['state', 'letters', 'actions', 'letters_solver', 'actions_solver']

# A list of all configs defined as globals,
# not assigned to any particular state.
other_configs = []

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!! Only keys defined in states_configs and other_configs
# will be visible in your application.!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# States transition matrix
state = number_of_states * [number_of_decisions * [0]]
state[0] = [0, 0, 0, 0, 0, 0, 0, 0]
state[1] = [1, 1, 1, 1, 1, 1, 1, 0]


# Letters definition for every state. Normally for every state it should be a collection of strings.
letters = number_of_states * [number_of_decisions * [""]]
letters[0] = [u"Naprzód", u"Do tyłu", u"W prawo", u'W lewo', '', '', '', 'Kolory']
letters[1] = [u"Żółty", "", "",  "",  "",  "",  "",  ""]

letters_solver = number_of_states * [number_of_decisions * [""]]

# actions[i][j] will be performed in state i when person is looking on square j
# If you wish no action - leave it empty.
# If you have a 'dynamic' state and you want the program to be chosen at runtime, set here a collection of programs -
# thanks to corresponding values from actions_solver obci will decide which program to use.
actions = number_of_states * [number_of_decisions * [""]]
actions[0] = ["robot('forward')", "robot('backward')", "robot('right')", "robot('left')", "robot('forward')", "robot('camera_up')", "robot('camera_middle')", "robot('camera_down')"]
actions[1] = ["set_field_color('yellow')", "","", "", "", "", "", ""]


actions_solver = number_of_states * [number_of_decisions * [""]]
