#!/usr/bin/env python
# -*- coding: utf-8 -*-

number_of_decisions = 8 #TODO - it should rather come from outside ...
number_of_states = 10

# A list of all configs defined for every single state.
states_configs = ['screen', 'graphics', 'graphics_solver', 
                  'actions', 'actions_solver']

# A list of all configs defined as globals, 
# not assigned to any particular state.
other_configs = []

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!! Only keys defined in states_configs and other_configs 
# will be visible in your application.!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# States transition matrix
screen = number_of_states * [number_of_decisions * [0]]
screen[0] = [1, 1, 1, 1, 1, 1, 1, 0]
screen[1] = [2, 3, 4, 5, 6, 7, 8, 0]
screen[2] = [2, 2, 2, 2, 2, 2, 2, 1]
screen[3] = [3, 3, 3, 3, 3, 3, 3, 1]
screen[4] = [4, 4, 4, 4, 4, 4, 4, 1]
screen[5] = [5, 5, 5, 5, 5, 5, 5, 1]
screen[6] = [6, 6, 6, 6, 6, 6, 6, 1]
screen[7] = [7, 7, 7, 7, 7, 7, 7, 1]
screen[8] = [8, 8, 8, 1, 8, 8, 8, 0]
screen[9] = [0, 9, 9, 9, 9, 9, 9, 9]

# Graphics definition for every state. Normally for every state it should be a collection of strings.
# Hovewever, sometimes we have a collection of strings, not a single string. It happens when we have a 'dynamic' state.
# In that case there should be a corresponding graphics_solver variable with method that resolves graphics definition at runtime.
graphics = number_of_states * [number_of_decisions * [""]]
graphics[0] = ["SSVEP", "P300", "ETR-PUNKT", "ETR-KURSOR" ,"WII","MYSZ","SPACJA",u"Zakończ"]
graphics[1] = [u"a b c d e f",u"g h i j k l",u"m n o p r s",u"t u w y z ż",u"ą ć ę ł ń ó ś", u"Znaki", u"Akcje", u"Menu"]
graphics[2] = ["a","b","c","d","e","f","Skasuj", u"Wróć"]
graphics[3] = ["g","h","i","j","k","l","Skasuj", u"Wróć"]
graphics[4] = ["m","n","o","p","r","s","Skasuj", u"Wróć"]
graphics[5] = ["t","u","w","y","z", u"ż","Skasuj", u"Wróć"]
graphics[6] = [u"ą", u"ć", u"ę", u"ł", u"ń", u"ś", u"ó", u"Wróć"]
graphics[7] = ["_",",",".",";","?","!","Skasuj",u"Wróć"]
graphics[8] = [u"Mów!",u"Wyczyść", u"Skasuj", u"Wróć", "", "", "", u"Menu"]
graphics[9] = [u"Wróć", "", "",  "",  "",  "",  "",  ""] 

# See descripton above.
graphics_solver = number_of_states * [number_of_decisions * [""]]
#graphics_solver[0] = ["solve_menu(0)", "solve_menu(1)", "solve_menu(2)","","","","",""]



# actions[i][j] will be performed in state i when person is looking on square j
# If you wish no action - leave it empty.
# If you have a 'dynamic' state and you want the program to be chosen at runtime, set here a collection of programs - 
# thanks to corresponding values from actions_solver obci will decide which program to use.
actions = number_of_states * [number_of_decisions * [""]]
        #action[0] = ['', '', '', 'python programDawida', '', '', 'python programDawida', '']
actions[0] = ["fire_speller('ssvep')", "fire_speller('p300')", "fire_speller('etr_classic')", 
              "fire_speller('etr_nesw')", "fire_speller('switch_wii')", 
              "fire_speller('switch_mouse')", "fire_speller('switch_space')", ""]
actions[1] = ["", "", "", "", "", "", "", ""] 
actions[2] = ["msg('a')", "msg('b')","msg('c')", "msg('d')", "msg('e')", "msg('f')", "backspace()", ""] 
actions[3] = ["msg('g')", "msg('h')", "msg('i')", "msg('j')", "msg('k')", "msg('l')", "backspace()", ""] 
actions[4] = ["msg('m')", "msg('n')", "msg('o')", "msg('p')", "msg('r')", "msg('s')", "backspace()", ""] 
actions[5] = ["msg('t')", "msg('u')", "msg('w')", "msg('y')", "msg('z')", u"msg(u'ż')", "backspace()", ""] 
actions[6] = [u"msg(u'ą')", u"msg(u'ć')", u"msg(u'ę')", u"msg(u'ł')", u"msg(u'ń')", u"msg(u'ś')", u"msg(u'ó')", ""]
actions[7] = ["msg(' ')", "msg(',')", "msg('.')", "msg(';')", "msg('?')", "msg('!')", "backspace()", ""]
actions[8] = ["say()", "clear()", "backspace()", "", "", "", "", ""]
actions[9] = ["close_dasher()", "", "", "", "", "", "", ""]

# See description above.
actions_solver = number_of_states * [number_of_decisions * [""]]
#actions_solver[0] = ["solve_menu(0)", "solve_menu(1)", "solve_menu(2)","","","","",""]
