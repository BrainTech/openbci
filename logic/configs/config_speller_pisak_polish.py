#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Config(object):
    def __init__(self):
        self.number_of_decisions = 37
        self.number_of_states = 2

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
        self.state[0] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0]
        self.state[1] = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1]

        # Graphics definition for every state. Normally for every state it should be a collection of strings.
        # Hovewever, sometimes we have a collection of strings, not a single string. It happens when we have a 'dynamic' state.
        # In that case there should be a corresponding graphics_solver variable with method that resolves graphics definition at runtime.
        self.letters = self.number_of_states * [self.number_of_decisions * [""]]
        self.letters[0] = ["A", "O", "N", "T", "D", "J",
                       "G", u"Ó", "I", "Z", "S", "K",
                       "U", "B", u"Ą", u"Ć", "E", "W",
                       "Y", "M", u"Ł", "H", u"Ś", u"Ń",
                       "R", "C", "P", "L", u"Ę", u"Ż",
                       "F", u"Ź", "POWIEDZ", u"USUŃ", "SPACJA", "ZNAKI", u"WYJDŹ"]
        self.letters[1] = ["1", "2", "3", "4", "5", "6",
                       "7", "8", "9", "0", "+", "-",
                       "*", "/", "=", "%", "$", "&",
                       ".", ",", ";", ":", "\"", "?",
                       "!", "@", "#", "(", ")", "[",
                       "]", "~", "POWIEDZ", u"USUŃ", "SPACJA", "ZNAKI", u"WYJDŹ"]

        # See descripton above.
        self.letters_solver = self.number_of_states * [self.number_of_decisions * [""]]

        # actions[i][j] will be performed in state i when person is looking on square j
        # If you wish no action - leave it empty.
        # If you have a 'dynamic' state and you want the program to be chosen at runtime, set here a collection of programs - 
        # thanks to corresponding values from actions_solver obci will decide which program to use.
        self.actions = self.number_of_states * [self.number_of_decisions * [""]]
        self.actions[0] = ["msg('')", "msg('O')", "msg('N')", "msg('T')", "msg('D')", "msg('J')", 
                      "msg('G')", u"msg(u'Ó')", "msg('I')", "msg('Z')", "msg('S')", "msg('K')", 
                      "msg('U')", "msg('B')", u"msg(u'Ą')", u"msg(u'Ć')", u"msg(u'Ę')", "msg('W')",
                      "msg('Y')", "msg('M')", u"msg(u'Ł')", "msg('H')", u"msg(u'Ś')", u"msg(u'Ń')",
                      "msg('R')", "msg('C')", "msg('P')", "msg('L')", u"msg(u'Ę')", u"msg(u'Ż')",
                      "msg('F')", u"msg(u'Ź')", "msg('nic0')", "backspace(2)", "msg(' ')", "update_board('pisak_polish_spell_bw')","update_board('pisak_polish_spell_bw')"]
        self.actions[1] = ["msg('1')", "msg('2')", "msg('3')", "msg('4')", "msg('5')", "msg('6')", 
                      "msg('7')", "msg('8')", "msg('9')", "msg('0')", "msg('+')", "msg('-')", 
                      "msg('*')", "msg('/')", "msg('=')", "msg('%')", "msg('$')", "msg('&')",
                      "msg('.')", "msg(',')", "msg(';')", "msg(':')", "msg('\"')", "msg('?')",
                      "msg('!')", "msg('@')", "msg('#')", "msg('(')", u"msg(u')')", u"msg(u'[')",
                      "msg(']')", u"msg(u'~')", "msg('nic0')", "backspace(2)", "msg(' ')", "update_board('pisak_polish_spell')","msg('nic2')"]

        # See description above.
        self.actions_solver = self.number_of_states * [self.number_of_decisions * [""]]

    def _finish_action(self):
        return "finish()"
