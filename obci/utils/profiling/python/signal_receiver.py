#!/usr/bin/env python
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2
import sys, time, numpy
import configurer


class Receiver(BaseMultiplexerServer):
    def __init__(self, addresses, duration, cache_size, dump_file, monitor_last_channel):
        self._configurer = configurer.Configurer(addresses)
        configs = self._configurer.get_configs(["NumOfChannels", "SamplesPerVector", "PEER_READY"+str(peers.AMPLIFIER)])
        self.number_of_channels = int(configs['NumOfChannels'])
        self.samples_per_vector = int(configs['SamplesPerVector'])
        if duration == 0: 
            self.duration = sys.float_info.max
        else:
            self.duration = duration
        self.cache_size = cache_size
        self.dump_file = dump_file
        if dump_file is not None:
            self.dump_file = open(dump_file, 'w')
        else:
            self.dump_file = None
        self.monitor_last_channel = monitor_last_channel

        self._prev_last_channel = 0
        self._samples_vector = variables_pb2.SampleVector()
        self._samples_count = 0
        self._start_ts = time.time()
        self._last_log_ts = 0.0
        self._last_log_count = 0
        self._cached_samples = numpy.zeros((self.number_of_channels, self.cache_size))
        self._cache_index = 0
        super(Receiver, self).__init__(addresses=addresses, type=peers.SIGNAL_STREAMER)
        self._configurer.set_configs({'PEER_READY':str(peers.SIGNAL_STREAMER)}, self.conn)

        print("Receiver initialsed! with num of channels: "+str(self.number_of_channels))

    def _dump_cache(self):
        pass
        #self._cached_samples.tofile(self.dump_file)
        #self.dump_file.write(str(self._cached_samples))
        #self.dump_file.flush()

    def handle_message(self, mxmsg):
        if mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:
            t = time.time()
            # write log
            if (t - self._last_log_ts) > 1:
                print("Number of samples of previous 1 sec: "+str(self._samples_count - self._last_log_count)+". Avg sampling: "+str(self._samples_count/(t - self._start_ts)))
                #print("Last sample: "+str(self._cached_samples[:, self._cache_index-1]))
                self._last_log_ts = t
                self._last_log_count = self._samples_count

            if (t - self._start_ts) > self.duration:
                print("Finishing...")
                sys.exit(0)

            self._samples_vector.ParseFromString(mxmsg.message)

            for i in range(self.samples_per_vector):
                self._samples_count += 1
                sample = self._samples_vector.samples[i]
                for j, ch in enumerate(sample.channels):
                    self._cached_samples[j, self._cache_index] = ch
            #print("GOT: "+str(self._cached_samples[0, self._cache_index]))

                if self.monitor_last_channel:
                    last_channel = self._cached_samples[self.number_of_channels-1][self._cache_index]
                    if self._prev_last_channel+1 != last_channel:
                        print("Lost samples in number: "+str(last_channel - self._prev_last_channel + 1));
                    self._prev_last_channel = last_channel;

                self._cache_index += 1
                if self._cache_index == self._cached_samples.shape[1]:
                    self._cache_index = 0
                    if self.dump_file is not None:
                        self._dump_cache()

        self.no_response()

if __name__ == "__main__":
    duration = 0
    cache_size = 1024
    dump_file = None
    host = "127.0.0.1"
    monitor_last_channel= 1
    if len(sys.argv) >= 2:
        duration = int(sys.argv[1])
    if len(sys.argv) >= 3:
        cache_size = int(sys.argv[2])
    if len(sys.argv) >= 4:
        dump_file = sys.argv[3]
    if len(sys.argv) >= 5:
        host = sys.argv[4]
    if len(sys.argv) >= 6:
        monitor_last_channel = int(sys.argv[5])



    f = Receiver([(host, 31889)], duration, cache_size, dump_file, monitor_last_channel == 1)
    f.loop()

