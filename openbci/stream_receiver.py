#!/usr/bin/env python
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, cPickle, collections, variables_pb2, os, sys


class StreamReceiver(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(StreamReceiver, self).__init__(addresses=addresses, type=peers.STREAM_RECEIVER)
        self.channels = "1 2 3" 
        self.conn.send_message(message=self.channels, type=types.SIGNAL_STREAMER_START, flush=True)       
        print "send start"
        self.index = 0
        self.stopped = False
        #self.file = open("new_stream1", 'w')

    def handle_message(self, mxmsg):
        if mxmsg.type == types.STREAMED_SIGNAL_MESSAGE:
            self.index += 1
            print "handle ",self.index
            #file = open("new_stream", 'w')
            #if (self.index <= 2):
            #    self.file.write(mxmsg.message)
            #file.close()
            #print mxmsg.message
            vector = variables_pb2.SampleVector()
            vector.ParseFromString(mxmsg.message)
            for s in vector.samples:
                print "value ",s.value, " timestamp ",s.timestamp
            # self.index += 1
            if (self.index >= 100):  #and (self.stopped == False):
                self.conn.send_message(message=" ", type=types.SIGNAL_STREAMER_STOP, flush=True)
                #self.file.close()
                #print "DONE"
                self.stopped = True

           

if __name__ == "__main__":
    StreamReceiver(settings.MULTIPLEXER_ADDRESSES).loop()
