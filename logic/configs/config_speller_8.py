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
        self.state[7] = [7, 7, 7, 0, 7, 7, 0, 0]

       # Letters definition for every state. Normally for every state it should be a collection of strings.
        self.letters = self.number_of_states * [self.number_of_decisions * [""]]
        self.letters[0] = [u"A B C\nD E F",u"G H I\nJ K L",u"M N O\nP R S",u"T U W\nX Y Z",u"Ą Ę Ł\nŃ Ó Ś", u"_,.;?!", u" akcje\nactions", u"  wróć\n  back    "]
        self.letters[1] = ["A","B","C","D","E","F","  skasuj  \ndelete", u"wróć\nback"]
        self.letters[2] = ["G","H","I","J","K","L","  skasuj  \ndelete", u"wróć\nback"]
        self.letters[3] = ["M","N","O","P","R","S","  skasuj  \ndelete", u"wróć\nback"]
        self.letters[4] = ["T","U","W","X","Y", u"Z","  skasuj  \ndelete", u"wróć\nback"]
        self.letters[5] = [u"ą", u"ę", u"ł", u"ń", u"ś", u"ó", "  skasuj  \ndelete", u"wróć\nback"]
        self.letters[6] = ["_ \nspace",", \ncomma",". \nperiod","; \nsemicolon","?????","!!!!!","  skasuj  \n  delete  ", u"wróć\nback"]
        self.letters[7] = [u"mów",u"wyczyść", u"skasuj", u"wróć", "say", "clear", "delete", "back"]

        self.letters_solver = self.number_of_states * [self.number_of_decisions * [""]]
        
        # actions[i][j] will be performed in state i when person is looking on square j
        # If you wish no action - leave it empty.
        # If you have a 'dynamic' state and you want the program to be chosen at runtime, set here a collection of programs - 
        # thanks to corresponding values from actions_solver obci will decide which program to use.
        self.actions = self.number_of_states * [self.number_of_decisions * [""]]
        self.actions[0] = ["", "", "", "", "", "", "", self._finish_action()] 
        self.actions[1] = ["msg('a')", "msg('b')","msg('c')", "msg('d')", "msg('e')", "msg('f')", "backspace()", ""] 
        self.actions[2] = ["msg('g')", "msg('h')", "msg('i')", "msg('j')", "msg('k')", "msg('l')", "backspace()", ""] 
        self.actions[3] = ["msg('m')", "msg('n')", "msg('o')", "msg('p')", "msg('r')", "msg('s')", "backspace()", ""] 
        self.actions[4] = ["msg('t')", "msg('u')", "msg('w')", "msg('x')", "msg('y')", u"msg(u'z')", "backspace()", ""] 
        self.actions[5] = [u"msg(u'ą')", u"msg(u'ę')", u"msg(u'ł')", u"msg(u'ń')", u"msg(u'ś')", u"msg(u'ó')", "backspace()", ""]
        self.actions[6] = ["msg(' ')", "msg(',')", "msg('.')", "msg(';')", "msg('?')", "msg('!')", "backspace()", ""]
        self.actions[7] = ["say()", "clear()", "backspace()", "", "say()", "clear()", "backspace()", ""]
        
        self.actions_solver = self.number_of_states * [self.number_of_decisions * [""]]

    def _finish_action(self):
        return "finish()"
