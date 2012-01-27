#!/usr/bin/env python
# -*- coding: utf-8 -*-

number_of_decisions = 8
number_of_states = 10

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
state[0] = [1, 9, 8, 0, 0, 0, 0, 0]
state[1] = [2, 3, 4, 5, 6, 7, 8, 0]
state[2] = [2, 2, 2, 2, 2, 2, 2, 1]
state[3] = [3, 3, 3, 3, 3, 3, 3, 1]
state[4] = [4, 4, 4, 4, 4, 4, 4, 1]
state[5] = [5, 5, 5, 5, 5, 5, 5, 1]
state[6] = [6, 6, 6, 6, 6, 6, 6, 1]
state[7] = [7, 7, 7, 7, 7, 7, 7, 1]
state[8] = [8, 8, 8, 1, 8, 8, 8, 0]
state[9] = [0, 9, 9, 9, 9, 9, 9, 9]

# Letters definition for every state. Normally for every state it should be a collection of strings.
letters = number_of_states * [number_of_decisions * [""]]
letters[0] = ["Speller", "Dasher", "Akcje", "" ,"","","",""]
letters[1] = [u"a b c d e f",u"g h i j k l",u"m n o p r s",u"t u w y z ż",u"ą ć ę ł ń ó ś", u"Znaki", u"Akcje", u"Menu"]
letters[2] = ["a","b","c","d","e","f","Skasuj", u"Wróć"]
letters[3] = ["g","h","i","j","k","l","Skasuj", u"Wróć"]
letters[4] = ["m","n","o","p","r","s","Skasuj", u"Wróć"]
letters[5] = ["t","u","w","y","z", u"ż","Skasuj", u"Wróć"]
letters[6] = [u"ą", u"ć", u"ę", u"ł", u"ń", u"ś", u"ó", u"Wróć"]
letters[7] = ["_",",",".",";","?","!","Skasuj",u"Wróć"]
letters[8] = [u"Mów!",u"Wyczyść", u"Skasuj", u"Wróć", "", "", "", u"Menu"]
letters[9] = [u"Wróć", "", "",  "",  "",  "",  "",  ""] 

letters_solver = number_of_states * [number_of_decisions * [""]]

# actions[i][j] will be performed in state i when person is looking on square j
# If you wish no action - leave it empty.
# If you have a 'dynamic' state and you want the program to be chosen at runtime, set here a collection of programs - 
# thanks to corresponding values from actions_solver obci will decide which program to use.
actions = number_of_states * [number_of_decisions * [""]]
actions[0] = ["", "run_ext('dasher &')", "", "", "", "", "", ""]
actions[1] = ["", "", "", "", "", "", "", ""] 
actions[2] = ["msg('a')", "msg('b')","msg('c')", "msg('d')", "msg('e')", "msg('f')", "backspace()", ""] 
actions[3] = ["msg('g')", "msg('h')", "msg('i')", "msg('j')", "msg('k')", "msg('l')", "backspace()", ""] 
actions[4] = ["msg('m')", "msg('n')", "msg('o')", "msg('p')", "msg('r')", "msg('s')", "backspace()", ""] 
actions[5] = ["msg('t')", "msg('u')", "msg('w')", "msg('y')", "msg('z')", u"msg(u'ż')", "backspace()", ""] 
actions[6] = [u"msg(u'ą')", u"msg(u'ć')", u"msg(u'ę')", u"msg(u'ł')", u"msg(u'ń')", u"msg(u'ś')", u"msg(u'ó')", ""]
actions[7] = ["msg(' ')", "msg(',')", "msg('.')", "msg(';')", "msg('?')", "msg('!')", "backspace()", ""]
actions[8] = ["say()", "clear()", "backspace()", "", "", "", "", ""]
actions[9] = ["close_dasher()", "", "", "", "", "", "", ""]

actions_solver = number_of_states * [number_of_decisions * [""]]
