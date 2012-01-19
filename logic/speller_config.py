number_of_decisions = 8 #TODO - it should rather come from outside ...
number_of_states = 8

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
screen[0] = [0, 0, 0, 1, 0, 0, 0, 0]
screen[1] = [1, 2, 3, 4, 5, 6, 7, 0]
screen[2] = [2, 2, 2, 2, 2, 2, 2, 1]
screen[3] = [3, 3, 3, 3, 3, 3, 3, 1]
screen[4] = [4, 4, 4, 4, 4, 4, 4, 1]
screen[5] = [5, 5, 5, 5, 5, 5, 5, 1]
screen[6] = [6, 6, 6, 6, 6, 6, 6, 1]
screen[7] = [7, 7, 7, 7, 7, 7, 7, 1]

# Graphics definition for every state. Normally for every state it should be a collection of strings.
# Hovewever, sometimes we have a collection of strings, not a single string. It happens when we have a 'dynamic' state.
# In that case there should be a corresponding graphics_solver variable with method that resolves graphics definition at runtime.
graphics = number_of_states * [number_of_decisions * [""]]
graphics[0] = [["light on", "light off"], 
               ["power on", "power off"], 
               ["power on", "power off"],
               "speller","","","",""]
graphics[1] = ["<","A B C D E F","G H I J K L","M N O P R S","T U W X Y Z","say","koniec","main"]
graphics[2] = ["<","A","B","C","D","E","F","back"]
graphics[3] = ["<","G","H","I","J","K","L","back"]
graphics[4] = ["<","M","N","O","P","R","S","back"]
graphics[5] = ["<","T","U","W","X","Y","Z","back"]
graphics[6] = ["<","say","V","W","X","Y","Z","back"]
graphics[7] = ["<","say",".",",","' '","","","back"]

# See descripton above.
graphics_solver = number_of_states * [number_of_decisions * [""]]
graphics_solver[0] = ["solve_menu(0)", "solve_menu(1)", "solve_menu(2)","","","","",""]



# actions[i][j] will be performed in state i when person is looking on square j
# If you wish no action - leave it empty.
# If you have a 'dynamic' state and you want the program to be chosen at runtime, set here a collection of programs - 
# thanks to corresponding values from actions_solver obci will decide which program to use.
actions = number_of_states * [number_of_decisions * [""]]
        #action[0] = ['', '', '', 'python programDawida', '', '', 'python programDawida', '']
actions[0] = [['run_ext(\'tahoe  "power on 1\\n\\r"\')', 'run_ext(\'tahoe  "power off 1\\n\\r"\')'], 
              ['run_ext(\'tahoe  "power on 2\\n\\r"\')', 'run_ext(\'tahoe  "power off 2\\n\\r"\')'], 
              ['run_ext(\'tahoe  "power on 3\\n\\r"\')', 'run_ext(\'tahoe  "power off 3\\n\\r"\')'], 
              "", "", "", "", ""]
actions[1] = ["backspace()", "", "", "", "", "say()", "", ""] 
actions[2] = ["backspace()", "msg('A')", "msg('B')", "msg('C')", "msg('D')", "msg('E')", "msg('F')", ""] 
actions[3] = ["backspace()", "msg('G')", "msg('H')", "msg('I')", "msg('J')", "msg('K')", "msg('L')", ""] 
actions[4] = ["backspace()", "msg('M')", "msg('N')", "msg('O')", "msg('P')", "msg('R')", "msg('S')", ""] 
actions[5] = ["backspace()", "msg('T')", "msg('U')", "msg('W')", "msg('X')", "msg('Y')", "msg('Z')", ""] 
actions[6] = ["backspace()", "say()", "", "", "", "", "", ""]
actions[7] = ["backspace()", "say()", "", "", "", "", "", ""]

# See description above.
actions_solver = number_of_states * [number_of_decisions * [""]]
actions_solver[0] = ["solve_menu(0)", "solve_menu(1)", "solve_menu(2)","","","","",""]
