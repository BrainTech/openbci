#!/usr/bin/env python

import math
import time, variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client


class VirtualEEGAmplifier:
    def __init__(self):
        self.connection = connect_client(type = peers.AMPLIFIER)
        self.function = self.connection.query(message="VirtualAmplifierFunction", type=types.DICT_GET_REQUEST_MESSAGE).message
        self.sampling_rate = int(self.connection.query(message="SamplingRate", type=types.DICT_GET_REQUEST_MESSAGE).message)
        self.channel_numbers = [int(x) for x in \
            self.connection.query(message="AmplifierChannelsToRecord", type=types.DICT_GET_REQUEST_MESSAGE).message.split(" ")]

        #self.file = open("start_stream", 'w')
    def do_sampling(self):
        offset = 0
        start_time = time.time()
        while True:
            channels_data = []
            for channel_number in self.channel_numbers:
                channels_data.append(eval(self.function))
            offset += 1
            sampleVector = variables_pb2.SampleVector()
            t = float(time.time())
            for x in channels_data:
                samp = sampleVector.samples.add()
                samp.value = float(x)
                samp.timestamp = float(t)
                #print "tstamp: ", samp.timestamp
                #print "val ",samp.value
            #for x in sampleVector.samples:
            #print "tstamp ", sampleVector.samples[0].timestamp
            #`print "val ", sampleVector.samples[0].value
            #if (offset <= 2):
            #    self.file.write(sampleVector.SerializeToString())
            #if (offset == 2):
            #    self.file.close()
#            channels_data_message = " ".join(str(x) for x in channels_data)
            # print sampleVector
            # print "break"

            self.connection.send_message(message=sampleVector.SerializeToString(), type=types.AMPLIFIER_SIGNAL_MESSAGE, flush=True)
            time_to_sleep = start_time + offset * (1. / self.sampling_rate) - time.time()
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)


if __name__ == "__main__":
    VirtualEEGAmplifier().do_sampling()

