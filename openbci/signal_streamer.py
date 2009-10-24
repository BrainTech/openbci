#!/usr/bin/env python

from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2


class SignalStreamer(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(SignalStreamer, self).__init__(addresses=addresses, type=peers.SIGNAL_STREAMER)
        self.state = 0 # temporarily: 0 = nothing; 1 = transmission
        self.channels = [0]
        self.subscribers = {}

    def handle_message(self, mxmsg):
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
            if self.state == 1:
                for node in self.subscribers:
                    channels = self.subscribers[node].split(" ")
                    sampVec = variables_pb2.SampleVector()
                    sampVec.ParseFromString(mxmsg.message)
                    newVec = variables_pb2.SampleVector()
                    for i in channels:
                        samp = newVec.samples.add()
                        samp.CopyFrom(sampVec.samples[int(i)])
                    self.conn.send_message(message=newVec.SerializeToString(), type=types.STREAMED_SIGNAL_MESSAGE, flush=True, to=int(node))  
                 
        elif mxmsg.type == types.SIGNAL_STREAMER_START:
            self.subscribers[str(mxmsg.from_)] = mxmsg.message
            self.state = 1
            self.no_response()
        elif mxmsg.type == types.SIGNAL_STREAMER_STOP:
           
            if str(mxmsg.from_) in self.subscribers:
                del self.subscribers[str(mxmsg.from_)]

            #self.state = 0
            self.no_response()
            


if __name__ == "__main__":
    SignalStreamer(settings.MULTIPLEXER_ADDRESSES).loop()
