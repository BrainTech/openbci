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

        self.robotIP = (self.conn.query(message = "RobotIP", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message
        screens = 2
        decisions = 9
        self.state = 0
        fields = 5

        # graph of menus
        self.screen = screens * [decisions * [0]]
        #                 0  1  2  3  4  5  6  7  8
        self.screen[0] = [0, 0, 0, 0, 0, 0, 0, 1, 0]
        self.screen[1] = [1, 1, 1, 1, 1, 1, 1, 0, 0]
       
       
        self.content = screens * [""]
        self.content[0] = "|::|::| :: | A B C D E :: | F G H I J:: | K L M N O :: | P R S T U:: | V W X Y Z :: | say ' ' . " 
        self.content[1] = " | :: | :: | :: | A :: | B :: | C :: | D :: | E :: | back "
        

        # move[state][decision] := path_to_robot

        self.move = screens * [decisions * ['']]
        self.move[0] = ["", "wget --spider http://" + self.robotIP + "/move/front_left", "", \
                        "wget --spider http://" + self.robotIP + "/move/left", "", "wget --spider http://" + self.robotIP + "/move/right", \
                        "", "", ""]
        self.move[1] = ["", "", "", \
                        "wget --spider http://" + self.robotIP + "/head/vert/-100", "", "wget --spider http://" + self.robotIP + "/head/vert/100", \
                        "", "", ""]
        
         
        self.message = ''
        self.pause = 0
        self.pausePoint = time.time()


    def handle_message(self, mxmsg):
        if mxmsg.type == types.DECISION_MESSAGE:
            decision = int(mxmsg.message)
            print "logic decision: ", decision
            if self.pause != 1:
                self.pausePoint = time.time()
                self.pause = 1
                if len(self.move[self.state[decision]]) > 0:
                    os.system(self.move[self.state[decision]])
            
                self.state = self.screen[self.state][decision]
                #print "self.state: ", self.state
                #print "content: ", self.content[self.state]
                self.conn.send_message(message = cPickle.dumps(["Panel", self.content[self.state]]), type = types.DICT_SET_MESSAGE, timeout = 0.1)
            elif time.time() - self.pausePoint > 2:
                self.pause = 0
        self.no_response() 

if __name__ == "__main__":
        SpellerLogic(settings.MULTIPLEXER_ADDRESSES).loop()
 
