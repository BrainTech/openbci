#!/usr/bin/env python

import time
import variables_pb2

from sample_logger import SampleLogger
import asizeof

class ProtobufTest(object):
    def __init__(self, samp_num=100000, channels_num=25, log_interval=100):

        print "Samples:  ", samp_num, " channels: ", channels_num,\
                " log_interval: ", log_interval
        
        self.num_of_samples = samp_num
        self.log_interval = log_interval
        self.num_of_channels = channels_num
        self.logger = SampleLogger(self.log_interval)

        self.sample_vec = variables_pb2.SampleVector()
        for x in range(1):#self.num_of_channels):
            samp = self.sample_vec.samples.add()
            for i in range(self.num_of_channels):
                samp.channels.append(float(x))
            samp.timestamp = time.time()

        self.msg = self.sample_vec.SerializeToString()
        print "Approx. serialized sample vector size: ", len(self.msg)


    def perform_packing_test(self):
        start_time = time.time()
        print "Start packing test: "
        self.logger.mark_start()
        for i in xrange(self.num_of_samples):
            samp = self.sample_vec.samples[0]
            # don`t do sth like: samp.channels[x] = float(x) without
            # clearing samp. Somehow, not-clearing samp results in linear memory usage...
            samp.Clear()
            for x in range(self.num_of_channels):
                samp.channels.append(float(x))
            samp.timestamp = time.time()
            msg = self.sample_vec.SerializeToString()
            #self.logger.log_sample()
        self.logger.mark_end()
        end_time = time.time()
        print "End of packing test - time: ", end_time - start_time,\
                " approx. sample rate: ", float(self.num_of_samples) / (end_time - start_time)
        data_size = len(self.msg) * self.num_of_samples
        print (float(data_size) / 1024 / 1024), " MiB"
        print (float(data_size) / (end_time - start_time) / 1000 / 1000 * 8), " Mbps"
        #self.logger.report()


    def perform_unpacking_test(self):
        start_time = time.time()
        test_vec = variables_pb2.SampleVector()
        msg = self.sample_vec.SerializeToString()
        print "Start deserializing test: "
        self.logger.mark_start()
        for i in xrange(self.num_of_samples):
            test_vec.ParseFromString(msg)
            #self.logger.log_sample()
        self.logger.mark_end()
        end_time = time.time()
        print "End of unpacking test - time: ", end_time - start_time,\
                " approx. sample rate: ", float(self.num_of_samples) / (end_time - start_time)
        #self.logger.report()
        data_size = len(self.msg) * self.num_of_samples
        print (float(data_size) / 1024 / 1024), " MiB"
        print (float(data_size) / (end_time - start_time) / 1000 / 1000 * 8), " Mbps"


if __name__ == "__main__":
    import sys
    #samp_num = 100
    #chan_num = 25
    #log_interval = 10
    if len(sys.argv) != 4:
        print("Usage: ./protobuf_test <num samples> <num channels> <log_interval>");
        sys.exit(0);

    samp_num = int(sys.argv[1])
    chan_num = int(sys.argv[2])
    log_interval = int(sys.argv[3])
    
    pt = ProtobufTest(samp_num=samp_num, 
            channels_num=chan_num, 
            log_interval=log_interval)

    pt.perform_packing_test()
    pt.perform_unpacking_test()
