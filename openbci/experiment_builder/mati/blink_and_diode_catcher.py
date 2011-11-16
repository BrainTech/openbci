#!/usr/bin/env python
#
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, cPickle, collections, variables_pb2, time

from openbci.core import  core_logging as logger
LOGGER = logger.get_logger("blink_and_diode_catcher", "info")

from openbci.tags import tagger
TAGGER = tagger.get_tagger()


class BlinkAndDiodeCatcher(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(BlinkAndDiodeCatcher, self).__init__(addresses=addresses, type=peers.BLINK_AND_DIODE_CATCHER)
        self.p300_state = ""
        self.ssvep_state = ""
    def get_state(self):
        return self.p300_state+self.ssvep_state

    def handle_message(self, mxmsg):
        if mxmsg.type == types.UGM_ENGINE_MESSAGE:
            m = variables_pb2.Variable()
            m.ParseFromString(mxmsg.message)
            print("GOT UGM ENGINE MESSAGE: "+m.key)
            if m.key == 'blinking_started':
                self.p300_state = "P300"
            elif m.key == 'blinking_stopped':
                self.p300_state = ""
                
        elif mxmsg.type == types.BLINK_MESSAGE:
            b = variables_pb2.Blink()
            b.ParseFromString(mxmsg.message)
            print("GOT BLINK: "+str(b.timestamp)+" / "+str(b.index))
            TAGGER.send_tag(b.timestamp, b.timestamp, "blink"+self.get_state(),
                            {"index" : b.index})

        elif mxmsg.type == types.DIODE_UPDATE_MESSAGE:
            m = variables_pb2.Variable()
            m.ParseFromString(mxmsg.message)
            m_val = max([int(i) for i in m.value.split(' ')])
            print("GOT DIODE UPDATE: "+str(m_val))
            if m_val == 0:
                t = time.time()
                TAGGER.send_tag(t, t, "diode_end"+self.get_state(),
                                {"freq" : m_val})
                self.ssvep_state = ""
            else:
                self.ssvep_state = "SSVEP"+str(m_val)

                t = time.time()
                TAGGER.send_tag(t, t, "diode_start"+self.get_state(),
                                {"freq" : m_val})


        self.no_response()


if __name__ == "__main__":
    BlinkAndDiodeCatcher(settings.MULTIPLEXER_ADDRESSES).loop()
