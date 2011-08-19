#!/usr/bin/env python
#
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, cPickle, collections, variables_pb2

from openbci.core import  core_logging as logger
LOGGER = logger.get_logger("blink_catcher", "info")

class BlinkCatcher(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(BlinkCatcher, self).__init__(addresses=addresses, type=peers.BLINK_CATCHER)
        self.buf_size =int(self.conn.query(message = "BlinkCatcherBufSize", type = types.DICT_GET_REQUEST_MESSAGE, timeout = 1).message)         

        self.buffer = collections.deque()
        self.prev = 0

    def handle_message(self, mxmsg):
        if mxmsg.type == types.BLINK_MESSAGE:
            b = variables_pb2.Blink()
            b.ParseFromString(mxmsg.message)
            print("GOT BLINK: time - "+str(b.timestamp)+" / time diff - "+str(b.timestamp - self.prev)+" / value - "+str(b.index))
            self.prev = b.timestamp
            self.buffer.append(mxmsg.message)
            LOGGER.info("GOT BLINK, buf len: "+str(len(self.buffer)))
            if (len(self.buffer) == self.buf_size):
                vector = variables_pb2.BlinkVector()
                for i in range(len(self.buffer)):
                    s = vector.blinks.add()
                    s.ParseFromString(self.buffer.popleft())
                LOGGER.info("Sending buffer...")
                self.conn.send_message(message = vector.SerializeToString(), type = types.BLINK_VECTOR_MESSAGE)
            else:
                self.no_response()


if __name__ == "__main__":
    BlinkCatcher(settings.MULTIPLEXER_ADDRESSES).loop()
