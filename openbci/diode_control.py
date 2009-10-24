#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy, cPickle, os, time, sys, random, samples_pb2, variables_pb2, blinker 
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer, connect_client

class DiodeControl:

    def __init__(self):

        self.connection = connect_client(type = peers.DIODE)
        # num of blinks per square
        self.blinks = int(self.connection.query(message = "Blinks", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) 
        # how long a blink should last
        self.blinkPeriod = float(self.connection.query(message = "BlinkPeriod", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message) 
        # num of squares into which display is devided
        self.squares = int(self.connection.query(message = "Squares", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.numOfRepeats = len(self.connection.query(message = "TrainingSequence", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message.split(" "))
        self.seq = []
        self.count = 0
    def generateSequence(self, blinks, squares, reps):
        seq = []
        for i in range(squares):
            [seq.append(i) for x in range(blinks * reps)]
        random.shuffle(seq)
        return seq
        

    def start(self):
        # 
        d = self.squares * [-1]
        
        # sequence to blink
        self.seq = self.generateSequence(self.blinks, self.squares, self.numOfRepeats)
        s = ""
        for x in self.seq:
            s += str(x) + ","
        s = s[:len(s) - 1]
        var = variables_pb2.Variable()
        var.key = "DiodSequence"
        var.value = s
        self.conn.send_message(message = var.SerializeToString(), type = types.DICT_SET_MESSAGE, flush=True)
        #self.connection.send_message(message = "", type = types.DIODE_MESSAGE, flush=True, timeout=1)
        for x in self.seq:
            blinker.blink_p300(x, 0.5)
            time.sleep(.75)
            tstamp = time.time()
            msg = variables_pb2.Blink()
            msg.index = x
            #self.count
            msg.timestamp = tstamp
            print "BLINK " 
            #str(self.count)
            #self.count += 1
            
            self.connection.send_message(message = msg.SerializeToString(), type = types.DIODE_MESSAGE, flush=True)
            print str(self.count)
            self.count += 1

if __name__ == "__main__":
   DiodeControl().start()


