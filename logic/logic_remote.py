#!/usr/bin/env python

import numpy, cPickle, os, time, sys, random, settings, time
from array import array
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client


class SpellerLogic(BaseMultiplexerServer):
    
    # states:  
    # -1: drops all messages
  
    def increaseChannel(self):
        self.channel += 1
        self.message = str(self.channel)

    def decreaseChannel(self):
        self.channel -= 1
        self.message = str(self.channel)

    def __init__(self, addresses):
        super(SpellerLogic, self).__init__(addresses=addresses, type=peers.LOGIC)
        self.numOfFreq = int(self.conn.query(message = "NumOfFreq", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        screens = 8
        decisions = 8
        self.state = 0
        fields = 5
        # graph of menus
        self.screen = screens * [decisions * [0]]
        #                 0  1  2  3  4  5  6  7  
        self.screen[0] = [0, 0, 0, 0, 0, 0, 0, 0]
        self.screen[1] = [1, 2, 3, 4, 5, 6, 7, 0]
        self.screen[2] = [2, 2, 2, 2, 2, 2, 2, 1]
        self.screen[3] = [3, 3, 3, 3, 3, 3, 3, 1]
        self.screen[4] = [4, 4, 4, 4, 4, 4, 4, 1]
        self.screen[5] = [5, 5, 5, 5, 5, 5, 5, 1]
        self.screen[6] = [6, 6, 6, 6, 6, 6, 6, 1]
        self.screen[7] = [7, 7, 7, 7, 7, 7, 7, 1]
        self.channel = 0

        self.action = screens * [decisions * ['']]

        # panel grphics[i] wille be presented on screen in state i
        self.graphics = screens * [""]
        self.graphics[0] = "| Wlacz :: | TV :: | W gore :: |  Zglosnij :: | Wylacz :: | Program  :: | W dol :: | Zcisz "

        self.graphics[1] = " | < :: | A B C D E :: | F G H I J:: | K L M N O :: | P R S T U:: | V W X Y Z :: | ' ' . :: | main"
        self.graphics[2] = " | < :: | say :: | A :: | B :: | C :: | D :: | E :: | back "
        self.graphics[3] = " | < :: | say :: | F :: | G :: | H :: | I :: | J :: | back "
        self.graphics[4] = " | < :: | say :: | K :: | L :: | M :: | N :: | O :: | back "
        self.graphics[5] = " | < :: | say :: | P :: | R :: | S :: | T :: | U :: | back "
        self.graphics[6] = " | < :: | say :: | V :: | W :: | X :: | Y :: | Z :: | back "
        self.graphics[7] = " | < :: | say :: | . :: | , :: | ' ' :: |  :: | :: | back "

        self.signs = screens * [self.decisions * [""]]
        
        # string signs[i][j] will be added to message in state i when person is looking at square j
        # if you wish no sign to be added leave it empty
        self.signs[0] = [', '', '', '', '', '', '', '']
        self.signs[1] = ['', '', 'A', 'B', 'C', 'D', 'E', ''] # taki smiec, ale potrzebny
        self.signs[2] = ['', '', 'A', 'B', 'C', 'D', 'E', '']
        self.signs[3] = ['', '', 'F', 'G', 'H', 'I', 'J', '']
        self.signs[4] = ['', '', 'K', 'L', 'M', 'N', 'O', '']
        self.signs[5] = ['', '', 'P', 'R', 'S', 'T', 'U', '']
        self.signs[6] = ['', '', 'V', 'W', 'X', 'Y', 'Z', '']
        self.signs[7] = ['', '', '.', ',', ' ',  '',  '', '']



        # action[i][j] will be performed in state i when person is looking on square j
        # if you wish no action - leave it emptyOA
        self.action = screens * [self.decisions * [""]]
        self.action[0] = ['', '', '', 'python programDawida', '', '', 'python programDawida', '']
        self.action[1] = ['', '', '', '', '', '', '', ''] 
        self.action[2] = ['', '', '', '', '', '', '', '']
        self.action[3] = ['', '', '', '', '', '', '', '']
        self.action[4] = ['', '', '', '', '', '', '', '']
        self.action[5] = ['', '', '', '', '', '', '', '']
        self.action[6] = ['', '', '', '', '', '', '', '']
        self.action[7] = ['', '', '', '', '', '', '', '']



        # function[i][j] : function to be dynamically called in state i when person looks at sq j

        self.function = screens * [self.decisions * [""]]
        self.function[0] = ['', '', '', 'self.increaseChannel', '', '', 'self.decreaseChannel', '']
        self.function[1] = ['', '', '', '', '', '', '', ''] 
        self.function[2] = ['', '', '', '', '', '', '', '']
        self.function[3] = ['', '', '', '', '', '', '', '']
        self.function[4] = ['', '', '', '', '', '', '', '']
        self.function[5] = ['', '', '', '', '', '', '', '']
        self.function[6] = ['', '', '', '', '', '', '', '']
        self.function[7] = ['', '', '', '', '', '', '', '']

        # params[i][j] : parameters with which action[i][j] will be called

        self.params = screens * [self.decisions * [""]]
        self.params[0] = ['', '', '', 'self.channel', '', '', 'self.channel', '']
        self.params[1] = ['', '', '', '', '', '', '', ''] 
        self.params[2] = ['', '', '', '', '', '', '', '']
        self.params[3] = ['', '', '', '', '', '', '', '']
        self.params[4] = ['', '', '', '', '', '', '', '']
        self.params[5] = ['', '', '', '', '', '', '', '']
        self.params[6] = ['', '', '', '', '', '', '', '']
        self.params[7] = ['', '', '', '', '', '', '', '']



        self.message = ''
        self.pause = 0
        self.pausePoint = time.time()


    def handle_message(self, mxmsg):
        if mxmsg.type == types.DECISION_MESSAGE:
            decision = int(mxmsg.message)
            if self.pause != 1:
		        self.pausePoint = time.time()
                self.pause = 1
                
                if (len(self.signs[self.state][decision]) > 0):
                    self.message = self.message + self.signs[self.state][decision]

                if (len(self.function[self.state][decision]) > 0):
                    eval(self.function[self.state][decision]())
                    

                if (len(self.action[self.state][decision]) > 0):
                    os.system(self.action[self.state][decision] + str(eval(self.params[self.state][decision])))

                 
                 
                 
                self.conn.send_message(message = cPickle.dumps(["Message", self.message]), type = types.DICT_SET_MESSAGE, flush=True)
                self.state = self.screen[self.state][decision]
                self.conn.send_message(message = cPickle.dumps(["Panel", self.graphics[self.state]]), type = types.DICT_SET_MESSAGE, flush = True)
            elif time.time() - self.pausePoint > 4:
                self.pause = 0
        self.no_response() 

if __name__ == "__main__":
        SpellerLogic(settings.MULTIPLEXER_ADDRESSES).loop()
 
