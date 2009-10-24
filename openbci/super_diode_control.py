#!/usr/bin/env python
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, cPickle, collections, variables_pb2, blinker, time, random


class SuperDiodeControl(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(SuperDiodeControl, self).__init__(addresses=addresses, type=peers.SUPER_DIODE)
        #self.buffer_size = int(self.conn.query(message="DiodeCatcherBufferSize", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.blinks = int(self.conn.query(message = "Blinks", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.blinkPeriod = float(self.conn.query(message = "BlinkPeriod", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
        self.squares = int(self.conn.query(message = "Squares", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)



        self.buffer = collections.deque()

    def start_blinking(self, freqs):
        d = []
        [d.append(int(x)) for x in freqs]
        blinker.blink(d, 1, 1)
    
    def diodes_on(self):
        d = self.squares * [0]
        blinker.blink(d, 1, 1)
    
    def diodes_off(self):
        d = self.squares * [-1]
        blinker.blink(d, 1, 1)
    
    def generateSequence(self, blinks, squares):
        seq = []
        for i in range(squares):
            [seq.append(i) for x in range(blinks)]
        random.shuffle(seq)
        return seq


    def handle_message(self, mxmsg):
        if mxmsg.type == types.SWITCH_MODE:
            self.mode = self.conn.query(message="BlinkingMode", type=types.DICT_GET_REQUEST_MESSAGE).message
            if (self.mode.lower() == "SSVEP".lower()):
                self.diodes_on()
                self.freqs = self.conn.query(message = "Freqs", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message
                self.freqs = self.freqs.split(" ")
                for i in range(len(self.freqs)):
                    self.freqs[i] = int(self.freqs[i])
                self.start_blinking(self.freqs)
            elif (self.mode.lower() == "P300".lower()):
                 self.diodes_off()
                 self.blinks = int(self.conn.query(message = "Blinks", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
                 self.blinkPeriod = float(self.conn.query(message = "BlinkPeriod", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
                 self.squares = int(self.conn.query(message = "Squares", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)
                 self.seq = self.generateSequence(self.blinks, self.squares)
                 self.conn.send_message(message = var.SerializeToString(), type = types.DICT_SET_MESSAGE, flush=True)
                 for x in self.seq:
                     blinker.blink_p300(x, self.blinkPeriod)
                     time.sleep(.75)
                     tstamp = time.time()
                     msg = variables_pb2.Blink()
                     msg.index = x
                        
                     msg.timestamp = tstamp
                     self.conn.send_message(message = msg.SerializeToString(), type = types.DIODE_MESSAGE, flush=True)
  
        self.no_response()


if __name__ == "__main__":
    SuperDiodeControl(settings.MULTIPLEXER_ADDRESSES).loop()
