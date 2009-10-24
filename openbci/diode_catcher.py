#!/usr/bin/env python
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, cPickle, collections


class DiodeCatcher(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(DiodeCatcher, self).__init__(addresses=addresses, type=peers.DIODE_CATCHER)
        #self.buffer_size = int(self.conn.query(message="DiodeCatcherBufferSize", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.buffer = collections.deque()

    def handle_message(self, mxmsg):
        if mxmsg.type == types.DIODE_REQUEST:
            if (len(self.buffer) > 0):
                self.send_message(message = self.buffer.popleft(), type = types.DIODE_RESPONSE)
            else:
                self.send_message(message = '', type = types.DIODE_RESPONSE)
        elif mxmsg.type == types.DIODE_MESSAGE:
            
            self.buffer.append(mxmsg.message)
            self.no_response()


if __name__ == "__main__":
    DiodeCatcher(settings.MULTIPLEXER_ADDRESSES).loop()
