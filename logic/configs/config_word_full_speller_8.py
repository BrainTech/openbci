#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Config(object):
    def __init__(self):
        self.number_of_decisions = 10
        self.number_of_states = 9
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
        self.state[0] = [1, 2, 3, 4, 5, 6, 7, 0, 8, 0]
        self.state[1] = [0, 0, 0, 0, 0, 0, 0, 0, 8, 0]
        self.state[2] = [0, 0, 0, 0, 0, 0, 0, 0, 8, 0]
        self.state[3] = [0, 0, 0, 0, 0, 0, 0, 0, 8, 0]
        self.state[4] = [0, 0, 0, 0, 0, 0, 0, 0, 8, 0]
        self.state[5] = [0, 0, 0, 0, 0, 0, 0, 0, 8, 0]
        self.state[6] = [0, 0, 0, 0, 0, 0, 0, 0, 8, 0]
        self.state[7] = [0, 0, 0, 0, 0, 0, 0, 0, 8, 0]
        self.state[8] = [8,8,8,8,8,8,8,8,8,0]

       # Letters definition for every state. Normally for every state it should be a collection of strings.
        self.letters = self.number_of_states * [self.number_of_decisions * [""]]
        self.letters[0] = [u"a ą b c\nć d e",u"ę f g h\ni j k",u"l ł m n\nń o ó",u"p q r s\nś t u",u"v w x y\nz ź ż", u"0 1 2 3\n4 5 6", u"7 8 9 ?\n  , - spacja", u"skasuj"]
        self.letters[1] = ["a", u"ą", "b", "c", u"ć", "d", "e", u"wróć"]
        self.letters[2] = [u"ę", u"f", "g", "h", u"i", "j", "k", u"wróć"]
        self.letters[3] = ["l", u"ł", "m", "n", u"ń", "o", u"ó", u"wróć"]
        self.letters[4] = ["p", "q", "r", "s", u"ś", "t", "u", u"wróć"]
        self.letters[5] = ["v", "w", "x", "y", "z", u"ź", u"ż", u"wróć"]
        self.letters[6] = ["0", "1", "2", "3", "4", "5", "6", u"wróć"]
        self.letters[7] = ["7", "8", "9", "?", ",", "_", "spacja", "back"]
        self.letters[8] = ['']*8

        self.letters_solver = self.number_of_states * [self.number_of_decisions * [""]]
        
        # actions[i][j] will be performed in state i when person is looking on square j
        # If you wish no action - leave it empty.
        # If you have a 'dynamic' state and you want the program to be chosen at runtime, set here a collection of programs - 
        # thanks to corresponding values from actions_solver obci will decide which program to use.
        self.actions = self.number_of_states * [self.number_of_decisions * [""]]
        self.actions[0] = ["", "", "", "", "", "", "", "word_backspace()"] 
        self.actions[1] = ["msg('a')", u"msg(u'ą')","msg('b')", "msg('c')", u"msg(u'ć')", "msg('d')", "msg('e')", ""] 
        self.actions[2] = [u"msg(u'ę')", "msg('f')", "msg('g')", "msg('h')", "msg('i')", "msg('j')", "msg('k')", ""] 
        self.actions[3] = ["msg('l')", u"msg(u'ł')", "msg('m')", "msg('n')", u"msg(u'ń')", "msg('o')", u"msg(u'ó')", ""] 
        self.actions[4] = ["msg('p')", "msg('q')", "msg('r')", "msg('s')", u"msg(u'ś')", "msg('t')", "msg('u')", ""] 
        self.actions[5] = ["msg('v')", "msg('w')", "msg('x')", "msg('y')", "msg('z')", u"msg(u'ź')", u"msg(u'ż')", ""]
        self.actions[6] = ["msg('0')", "msg('1')", "msg('2')", "msg('3')", "msg('4')", "msg('5')", "msg('6')", ""]
        self.actions[7] = ["msg('7')", "msg('8')", "msg('9')", "msg('?')", "msg(',')", "msg('-')", "msg(' ')", ""]
        self.actions[8] = ['']*8
        
        self.actions_solver = self.number_of_states * [self.number_of_decisions * [""]]

    def _finish_action(self):
        return "finish()"
