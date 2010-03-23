from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings
import tagger
TAGGER = tagger.get_tagger()

class TestTagsReceiver(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(TestTagsReceiver, self).__init__(addresses=addresses, 
                                          type=peers.TAGS_RECEIVER)
    def handle_message(self, mxmsg):
        print("TestTagsReceiver got message type: ", mxmsg.type)
        if mxmsg.type == types.TAG:
            print("Try unpacking tag...")
            l_tag_dict = TAGGER.unpack_tag(mxmsg.message)
            print(l_tag_dict)
if __name__ == "__main__":
    TestTagsReceiver(settings.MULTIPLEXER_ADDRESSES).loop()


        
