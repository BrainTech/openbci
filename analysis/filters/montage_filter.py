#!/usr/bin/env python
from Numeric import *
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2

class Filter(BaseMultiplexerServer):
    def __init__(self, addresses):
        super(Filter, self).__init__(addresses=addresses, type=peers.FILTER)
        montage_path = ''.join([settings.module_abs_path(), "montage.list"])
        print(montage_path)
        #channels_path = "channels.list"
        lines = file(montage_path).readlines()
	print lines
        # chann = file(channels.path).readline() 
	
        self.macierz = array([[float(x) for x in line.strip(" \n").split(" ")] for line in lines])
        #channels = [int(x) for x in chann.strip(" \n").split(" ")]

    def handle_message(self, mxmsg):
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
	    vec = variables_pb2.SampleVector()
	    vec.ParseFromString(mxmsg.message)
            d = []
	    for x in vec.samples:
		d.append(x.value)   
	    
		
            # d = cPickle.loads(mxmsg.message)
            # d = list(d)
	    # print d
	    # print self.macierz
            res = matrixmultiply([d], self.macierz)[0]
            # s = " ".join(str(x) for x in list(res))
	    for i in range(len(vec.samples)):
		vec.samples[i].value = res[i] 
            self.conn.send_message(message=vec.SerializeToString(), type=types.FILTERED_SIGNAL_MESSAGE, flush=True)

            #self.conn.send_message(message=mxmsg.message, type=types.FILTERED_SIGNAL_MESSAGE, flush=True)
            self.no_response()


if __name__ == "__main__":
    Filter(settings.MULTIPLEXER_ADDRESSES).loop()
