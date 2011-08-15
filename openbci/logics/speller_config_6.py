#!/usr/bin/env python
# -*- coding: utf-8 -*-

number_of_decisions = 6 #TODO - it should rather come from outside ...
number_of_states = 11

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
screen[0] = [1, 10, 7, 0, 0, 0]
screen[1] = [2, 3, 4, 7, 6, 5]
screen[2] = [8, 9, 2, 1, 2, 2]
screen[3] = [3, 3, 3, 1, 3, 3]
screen[4] = [4, 4, 4, 1, 4, 4]
screen[5] = [5, 5, 5, 1, 5, 5]
screen[6] = [6, 6, 6, 1, 6, 6]
screen[7] = [7, 7, 0, 1, 7, 7]
screen[8] = [8, 8, 8, 2, 8, 8]
screen[9] = [9, 9, 9, 2, 9, 9]
screen[10] = [0, 10, 10, 10, 10, 10]

# Graphics definition for every state. Normally for every state it should be a collection of strings.
# Hovewever, sometimes we have a collection of strings, not a single string. It happens when we have a 'dynamic' state.
# In that case there should be a corresponding graphics_solver variable with method that resolves graphics definition at runtime.
graphics = number_of_states * [number_of_decisions * [""]]
graphics[0] = [
               "Speller","Dasher","Akcje",
#["light on", "light off"], 
               #["power on", "power off"], 
               #["power on", "power off"],
               "","",""]
graphics[1] = [u"ą-ń ś-ż a b c","d e f g h","i j k l m", "Akcje", "t u w y z", "n o p r s"]
graphics[2] = [u"a-ń",u"ś-ż","a",u"Wróć","c","b"]
graphics[3] = ["d","e","f",u"Wróć","h","g"]
graphics[4] = ["i","j","k",u"Wróć","m","l"]
graphics[5] = ["n", "o", "p", u"Wróć","s","r"]
graphics[6] = ["t", "u","w",u"Wróć","z","y"]
graphics[7] = ["<","_", u"Menu Główne",u"Wróć", u"Wyczyść", u"Mów!"]
graphics[8] = [u"ą", u"ć", u"ę", u"Wróć", u"ń", u"ł"]
graphics[9] = [u"ś", u"ó", u"ź", u"Wróć", "", u"ż"]
graphics[10] = [u"Wróć", "", "", "", "", ""]

# See descripton above.
graphics_solver = number_of_states * [number_of_decisions * [""]]
#graphics_solver[0] = ["solve_menu(0)", "solve_menu(1)", "solve_menu(2)","","",""]



# actions[i][j] will be performed in state i when person is looking on square j
# If you wish no action - leave it empty.
# If you have a 'dynamic' state and you want the program to be chosen at runtime, set here a collection of programs - 
# thanks to corresponding values from actions_solver obci will decide which program to use.
actions = number_of_states * [number_of_decisions * [""]]
        #action[0] = ['', '', '', 'python programDawida', '', '', 'python programDawida', '']
actions[0] = [#['run_ext(\'tahoe  "power on 1\\n\\r"\')', 'run_ext(\'tahoe  "power off 1\\n\\r"\')'], 
              #['run_ext(\'tahoe  "power on 2\\n\\r"\')', 'run_ext(\'tahoe  "power off 2\\n\\r"\')'], 
              #['run_ext(\'tahoe  "power on 3\\n\\r"\')', 'run_ext(\'tahoe  "power off 3\\n\\r"\')'], 
              "", "run_ext('dasher &')", "", "", "", ""]
actions[1] = ["", "", "", "", "", ""] 
actions[2] = ["", "", "msg('a')", "","msg('c')", "msg('b')"] 
actions[3] = ["msg('d')", "msg('e')", "msg('f')", "","msg('h')", "msg('g')"] 
actions[4] = ["msg('i')", "msg('j')", "msg('k')", "", "msg('m')", "msg('l')"] 
actions[5] = ["msg('n')", "msg('o')", "msg('p')", "","msg('s')", "msg('r')"] 
actions[6] = ["msg('t')", "msg('u')",  "msg('w')", "", "msg('z')", "msg('y')"]
actions[7] = ["backspace()", "msg(' ')", "", "", "clear()", "say()"]
actions[8] = [u"msg(u'ą')", u"msg(u'ć')", u"msg(u'ę')", "", u"msg(u'ń')", u"msg(u'ł')"]
actions[9] = [u"msg(u'ś')", u"msg(u'ó')", u"msg(u'ź')", "", "", u"msg(u'ż')"]
actions[10] = ["close_dasher()", "", "", "", "", ""]

# See description above.
actions_solver = number_of_states * [number_of_decisions * [""]]
#actions_solver[0] = ["solve_menu(0)", "solve_menu(1)", "solve_menu(2)","","",""]
