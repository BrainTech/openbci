#!/usr/bin/env python

import numpy, cPickle, os, time, sys, random, settings, time
from array import array
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client


class SpellerLogic(BaseMultiplexerServer):
    
    # states:  
    # -1: drops all messages
  
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
        self.screen[0] = [0, 0, 1, 0, 0, 0, 0, 0]
        self.screen[1] = [1, 2, 3, 4, 5, 6, 7, 0]
        self.screen[2] = [2, 2, 2, 2, 2, 2, 2, 1]
        self.screen[3] = [3, 3, 3, 3, 3, 3, 3, 1]
        self.screen[4] = [4, 4, 4, 4, 4, 4, 4, 1]
        self.screen[5] = [5, 5, 5, 5, 5, 5, 5, 1]
        self.screen[6] = [6, 6, 6, 6, 6, 6, 6, 1]
        self.screen[7] = [7, 7, 7, 7, 7, 7, 7, 1]


        self.content = screens * [""]
        self.content[0] = "| ligth on :: | sound on :: | speller :: |  :: | light off :: | sound off  :: |  :: | "

        self.content[1] = " | < :: | A B C D E :: | F G H I J:: | K L M N O :: | P R S T U:: | V W X Y Z :: | ' ' . :: | main"
        self.content[2] = " | < :: | say :: | A :: | B :: | C :: | D :: | E :: | back "
        self.content[3] = " | < :: | say :: | F :: | G :: | H :: | I :: | J :: | back "
        self.content[4] = " | < :: | say :: | K :: | L :: | M :: | N :: | O :: | back "
        self.content[5] = " | < :: | say :: | P :: | R :: | S :: | T :: | U :: | back "
        self.content[6] = " | < :: | say :: | V :: | W :: | X :: | Y :: | Z :: | back "
        self.content[7] = " | < :: | say :: | . :: | , :: | ' ' :: |  :: | :: | back "

        self.signs = screens * [self.numOfFreq * [""]]
        
        self.signs[0] = ['power on 1 \n\r', 'power on 2\n\r', '', '', 'power off 1\n\r', 'power off 2\n\r', '', '']
        self.signs[1] = ['', '', 'A', 'B', 'C', 'D', 'E', ''] # taki smiec, ale potrzebny
        self.signs[2] = ['', '', 'A', 'B', 'C', 'D', 'E', '']
        self.signs[3] = ['', '', 'F', 'G', 'H', 'I', 'J', '']
        self.signs[4] = ['', '', 'K', 'L', 'M', 'N', 'O', '']
        self.signs[5] = ['', '', 'P', 'R', 'S', 'T', 'U', '']
        self.signs[6] = ['', '', 'V', 'W', 'X', 'Y', 'Z', '']
        self.signs[7] = ['', '', '.', ',', ' ',  '',  '', '']

        self.message = ''
        self.pause = 0
        self.pausePoint = time.time()


    def handle_message(self, mxmsg):
        if mxmsg.type == types.DECISION_MESSAGE:
            decision = int(mxmsg.message)
            print "logic decision: ", decision, " self.state ", self.state, " signs ", self.signs[self.state][decision]
            if self.pause != 1:
		print "action ", self.signs[self.state][decision] 
                self.pausePoint = time.time()
                self.pause = 1
                if (self.state == 0):
                    if len(self.signs[0][decision]):
                        os.system("tahoe '" + self.signs[0][decision] + "'")

                elif decision == 0: #backspace
                    self.message = self.message[:len(self.message) - 1]
                    self.conn.send_message(message = cPickle.dumps(["Message", self.message]), type = types.DICT_SET_MESSAGE, timeout = 0.1)
                elif (self.state > 1 and self.state < 7) and (decision > 1 and decision < 7):
                    self.message = self.message + self.signs[self.state][decision] 
                    self.conn.send_message(message = cPickle.dumps(["Message", self.message]), type = types.DICT_SET_MESSAGE, flush=True)
                elif (self.state > 0 and decision == 1):
                    os.system("milena_say " + self.message)
                
                self.state = self.screen[self.state][decision]
                #print "self.state: ", self.state
                #print "content: ", self.content[self.state]
                self.conn.send_message(message = cPickle.dumps(["Panel", self.content[self.state]]), type = types.DICT_SET_MESSAGE, flush = True)
            elif time.time() - self.pausePoint > 4:
                self.pause = 0
        self.no_response() 

if __name__ == "__main__":
        SpellerLogic(settings.MULTIPLEXER_ADDRESSES).loop()
 
