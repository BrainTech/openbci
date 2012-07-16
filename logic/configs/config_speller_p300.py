#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Config(object):
    def __init__(self):
        self.number_of_decisions = 36
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
        self.letters = [["A", "B", "C", "D", "E", "F",
                       "G", "H", "I", "J", "K", "L",
                       "M", "N", "O", "P", "R", "S",
                       "T", "U", "W", "Y", "Z", "0",
                       "1", "2", "3", "4", "5", "6",
                       "7", "8", "9", "_", "<-", "#"]]

        # See descripton above.
        self.letters_solver = [[""]*self.number_of_decisions]

        # actions[i][j] will be performed in state i when person is looking on square j
        # If you wish no action - leave it empty.
        # If you have a 'dynamic' state and you want the program to be chosen at runtime, set here a collection of programs - 
        # thanks to corresponding values from actions_solver obci will decide which program to use.
        self.actions = [["msg('A')", "msg('B')", "msg('C')", "msg('D')", "msg('E')", "msg('F')", 
                      "msg('G')", "msg('H')", "msg('I')", "msg('J')", "msg('K')", "msg('L')", 
                      "msg('M')", "msg('N')", "msg('O')", "msg('P')", "msg('R')", "msg('S')",
                      "msg('T')", "msg('U')", "msg('W')", "msg('Y')", "msg('Z')", "msg('0')",
                      "msg('1')", "msg('2')", "msg('3')", "msg('4')", "msg('5')", "msg('6')",
                      "msg('7')", "msg('8')", "msg('9')", "msg(' ')", "backspace()", "say()"]]

        # See description above.
        self.actions_solver = [[""]*self.number_of_decisions]

    def _finish_action(self):
        return "finish()"
