#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Config(object):
    def __init__(self):
        self.number_of_decisions = 8
        self.number_of_states = 8
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
        self.state[0] = [1, 2, 3, 4, 5, 6, 7, 0]
        self.state[1] = [1, 1, 1, 1, 1, 1, 1, 0]
        self.state[2] = [2, 2, 2, 2, 2, 2, 2, 0]
        self.state[3] = [3, 3, 3, 3, 3, 3, 3, 0]
        self.state[4] = [4, 4, 4, 4, 4, 4, 4, 0]
        self.state[5] = [5, 5, 5, 5, 5, 5, 5, 0]
        self.state[6] = [6, 6, 6, 6, 6, 6, 6, 0]
        self.state[7] = [7, 7, 7, 1, 7, 7, 7, 0]
        self.state[8] = [0, 8, 8, 8, 8, 8, 8, 8]

       # Letters definition for every state. Normally for every state it should be a collection of strings.
        self.letters = self.number_of_states * [self.number_of_decisions * [""]]
        self.letters[0] = [u"a b c d e f",u"g h i j k l",u"m n o p r s",u"t u w y z ż",u"ą ć ę ł ń ó ś", u"Znaki", u"Akcje", u"Menu"]
        self.letters[1] = ["a","b","c","d","e","f","Skasuj", u"Wróć"]
        self.letters[2] = ["g","h","i","j","k","l","Skasuj", u"Wróć"]
        self.letters[3] = ["m","n","o","p","r","s","Skasuj", u"Wróć"]
        self.letters[4] = ["t","u","w","y","z", u"ż","Skasuj", u"Wróć"]
        self.letters[5] = [u"ą", u"ć", u"ę", u"ł", u"ń", u"ś", u"ó", u"Wróć"]
        self.letters[6] = ["_",",",".",";","?","!","Skasuj",u"Wróć"]
        self.letters[7] = [u"Mów!",u"Wyczyść", u"Skasuj", u"Wróć", "", "", "", u"Menu"]
        self.letters[8] = [u"Wróć", "", "",  "",  "",  "",  "",  ""] 

        self.letters_solver = self.number_of_states * [self.number_of_decisions * [""]]

        # actions[i][j] will be performed in state i when person is looking on square j
        # If you wish no action - leave it empty.
        # If you have a 'dynamic' state and you want the program to be chosen at runtime, set here a collection of programs - 
        # thanks to corresponding values from actions_solver obci will decide which program to use.
        self.actions = self.number_of_states * [self.number_of_decisions * [""]]
        self.actions[0] = ["", "", "", "", "", "", "", "finish("+self._finish_params()+")"] 
        self.actions[1] = ["msg('a')", "msg('b')","msg('c')", "msg('d')", "msg('e')", "msg('f')", "backspace()", ""] 
        self.actions[2] = ["msg('g')", "msg('h')", "msg('i')", "msg('j')", "msg('k')", "msg('l')", "backspace()", ""] 
        self.actions[3] = ["msg('m')", "msg('n')", "msg('o')", "msg('p')", "msg('r')", "msg('s')", "backspace()", ""] 
        self.actions[4] = ["msg('t')", "msg('u')", "msg('w')", "msg('y')", "msg('z')", u"msg(u'ż')", "backspace()", ""] 
        self.actions[5] = [u"msg(u'ą')", u"msg(u'ć')", u"msg(u'ę')", u"msg(u'ł')", u"msg(u'ń')", u"msg(u'ś')", u"msg(u'ó')", ""]
        self.actions[6] = ["msg(' ')", "msg(',')", "msg('.')", "msg(';')", "msg('?')", "msg('!')", "backspace()", ""]
        self.actions[7] = ["say()", "clear()", "backspace()", "", "", "", "", ""]
        
        self.actions_solver = self.number_of_states * [self.number_of_decisions * [""]]

    def _finish_params(self):
        return "x, x"
