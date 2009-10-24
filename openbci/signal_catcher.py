#!/usr/bin/env python
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, cPickle, collections, variables_pb2


class SignalCatcher(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(SignalCatcher, self).__init__(addresses=addresses, type=peers.SIGNAL_CATCHER)
        self.number_of_channels = len(self.conn.query(message="AmplifierChannelsToRecord", type=types.DICT_GET_REQUEST_MESSAGE).message.split(" "))
        self.buffer = [collections.deque() for z in range(self.number_of_channels)]
        self.buffer_size = int(self.conn.query(message="SignalCatcherBufferSize", type=types.DICT_GET_REQUEST_MESSAGE).message)

    def add(self, value):
        #print "ADD"
        sampleVector = variables_pb2.SampleVector()
        #print "UWAGA"
        sampleVector.ParseFromString(value)
        #print sampleVector
        values = sampleVector.samples
        #for x in values:
        #    print "sc ", float(x.timestamp)
        #    print "sc val ", float(x.value)
        #print "SC: ",values[0].timestamp
        #print "SC val: ",values[0].value
        # buffer[i] = buffer_size samples from channel i
        i = 0
        for s in values:
            self.buffer[i].append(s)
            if len(self.buffer[i]) > self.buffer_size:
                self.buffer[i].popleft()
            i += 1

        

    def handle_message(self, mxmsg):
        if mxmsg.type == types.SIGNAL_CATCHER_REQUEST_MESSAGE:
            vector = variables_pb2.SampleVector()
            ind = int(mxmsg.message)
            for i in range(len(self.buffer[ind])):
                s = vector.samples.add()
                s.CopyFrom(self.buffer[ind][i])
            self.send_message(message = vector.SerializeToString(), type = types.SIGNAL_CATCHER_RESPONSE_MESSAGE)
        #elif mxmsg.type == types.FILTERED_SIGNAL_MESSAGE:
        elif mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
            self.add(mxmsg.message)
            self.no_response()


if __name__ == "__main__":
    SignalCatcher(settings.MULTIPLEXER_ADDRESSES).loop()
