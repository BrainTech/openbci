#!/usr/bin/env python

import time, random, sys
import variables_pb2
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import connect_client

INTERVAL_FIX_CONSTANT = 1.0 # 0.97 - 128, 0.88 - 512, 0.79 - 1024 - sampling timing is not very accurate in python, so we need 'tune' it by fixed constant...
class VirtualAmplifier(object):
    def __init__(self, number_of_channels, sampling_frequency, duration, values_type):
        self.number_of_channels = number_of_channels
        self.sampling_frequency = sampling_frequency
        if duration == 0:
            self.duration = sys.float_info.max
        else:
            self.duration = duration

        #0 - sequential number, 1 - random numbers
        self.values_type = values_type
        self._init_connection()
        self._init_rest()

    def _init_connection(self):
        self.connection = connect_client(type = peers.AMPLIFIER)
        self._set_hashtable_value("SamplingRate", str(self.sampling_frequency))
        self._set_hashtable_value("NumOfChannels", str(self.number_of_channels))
        self._set_hashtable_value("Gain", ' '.join(['1.0']*self.number_of_channels))
        self._set_hashtable_value("Offset", ' '.join(['0.0']*self.number_of_channels))
        self._set_hashtable_value("ChannelsNames", ';'.join([str(i) for i in range(self.number_of_channels)]))

    def _set_hashtable_value(self, key, value):
        l_var = variables_pb2.Variable()
        l_var.key = key
        l_var.value = value
        self.connection.send_message(message = l_var.SerializeToString(), 
                                     type = types.DICT_SET_MESSAGE, flush=True)

    def _init_rest(self):
        self._samples_count = 0
        self._sample_interval = (1/float(self.sampling_frequency))*INTERVAL_FIX_CONSTANT
        self._start_ts = time.time()
        self._last_log_ts = 0.0
        self._last_log_count = 0

        t = time.time()
        if self.values_type == 0: v = float(self._samples_count) 
        else: v = random.random()

        self._samples_vector = variables_pb2.SampleVector()
        for x in range(self.number_of_channels):
            samp = self._samples_vector.samples.add()
            samp.value = v
            samp.timestamp = t


                                 
    def do_sampling(self):
        print("Start samples sampling.")
        while True:
            #send current message
            print("Send: "+str(self._samples_vector.samples[0].value))
            last_sent_time = time.time()
            self.connection.send_message(
                message=self._samples_vector.SerializeToString(), 
                type=types.AMPLIFIER_SIGNAL_MESSAGE, flush=True)
            self._samples_count += 1.0


            if (last_sent_time - self._last_log_ts) > 1:
                print("Number of samples of previous 1 sec: "+str(self._samples_count - self._last_log_count))
                print("Avg sampling: "+str(self._samples_count/(last_sent_time - self._start_ts)))
                self._last_log_ts = last_sent_time
                self._last_log_count = self._samples_count

            if (last_sent_time - self._start_ts) > self.duration:
                break

            #generate next message
            if self.values_type == 0: v = float(self._samples_count) 
            else: v = random.random()

            for i in range(self.number_of_channels):
                samp = self._samples_vector.samples[i]
                samp.value = v
                samp.timestamp = last_sent_time 
                #a little fake timestamp, should be set just before self.connection.send_message
                #it is made like that so that maximum accuracy for sampling is provided
                
            #wait if have some time
            time_to_sleep = self._sample_interval - (time.time() - last_sent_time)
            if time_to_sleep > 0:
                time.sleep(time_to_sleep)



        print("Sampling finished.")

if __name__ == "__main__":
    number_of_channels = 25
    sampling = 64
    duration = 5
    values_type = 0
    print(sys.argv)
    if len(sys.argv) >= 2:
        number_of_channels = int(sys.argv[1])
    if len(sys.argv) >= 3:
        sampling = int(sys.argv[2])
    if len(sys.argv) >= 4:
        duration = int(sys.argv[3])
    if len(sys.argv) >= 5:
        values_type = int(sys.argv[4])

    amp = VirtualAmplifier(number_of_channels, sampling, duration, values_type)
    amp.do_sampling()
