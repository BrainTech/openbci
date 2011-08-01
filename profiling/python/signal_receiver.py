#!/usr/bin/env python
from multiplexer.multiplexer_constants import peers, types
from multiplexer.clients import BaseMultiplexerServer
import settings, variables_pb2
import sys, time, numpy


class Receiver(BaseMultiplexerServer):
    def __init__(self, addresses, duration, cache_size, dump_file, monitor_last_channel):
        self._cache_index = -1
        super(Receiver, self).__init__(addresses=addresses, type=peers.SIGNAL_STREAMER)
        self.number_of_channels = int(self.conn.query(
                message="NumOfChannels", 
                type=types.DICT_GET_REQUEST_MESSAGE).message)

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
        print("Receiver initialsed!")

    def _dump_cache(self):
        pass
        #self._cached_samples.tofile(self.dump_file)
        #self.dump_file.write(str(self._cached_samples))
        #self.dump_file.flush()

    def handle_message(self, mxmsg):
        if self._cache_index == -1:
            pass
        elif mxmsg.type == types.AMPLIFIER_SIGNAL_MESSAGE:

            self._samples_count += 1

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
            #if self._samples_count == 1:
            #    time.sleep(10)
            #cache data
            for i, i_sample in enumerate(self._samples_vector.samples):
                self._cached_samples[i, self._cache_index] = i_sample.value
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

