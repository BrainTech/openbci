#!/usr/bin/env python
# -*- coding: utf-8 -*-
import collections
import ring_buffer_numpy_channels

class Blink(object):
    def __init__(self,blink,blink_count, blink_pos):
        self.blink = blink
        self.count = blink_count
        self.position = blink_pos
    
class Sample(object):
    def __init__(self, num_of_channels):
        self.channels = [0]*num_of_channels

class AutoBlinkBuffer(object):
    def __init__(self, from_blink, samples_count, num_of_channels, sampling, ret_func, ret_format, copy_on_ret):
        
        assert(samples_count > 0)
        assert(num_of_channels > 0)
        assert(ret_format in ['PROTOBUF_SAMPLES', 'NUMPY_CHANNELS'])

        self.ret_func = ret_func
        self.ret_buf_len = samples_count #1024
        self.blink_from = from_blink #-128
        self.sampling = sampling #float(1024)
        self.curr_blink = None
        self.curr_blink_ts = None
        self.count = 0
        self.blinks_count = 0
        self.is_full = False
        self.whole_buf_len = (self.ret_buf_len + abs(self.blink_from))*2 #2 in case blink comes not in real-time

        if ret_format == 'PROTOBUF_SAMPLES':
            import ring_buffer_protobuf_samples
            self.buffer = ring_buffer_protobuf_samples.RingBufferProtobufSamples(self.whole_buf_len, num_of_channels, copy_on_ret)
        elif ret_format == 'NUMPY_CHANNELS':
            self.buffer = ring_buffer_numpy_channels.RingBufferNumpyChannels(self.whole_buf_len, num_of_channels, copy_on_ret)

        self.times = ring_buffer_numpy_channels.RingBufferNumpyChannels(self.whole_buf_len, 1, copy_on_ret)
        self.times_sample = Sample(1)
        self.blinks = collections.deque()

    def clear(self):
        self.count = 0
        self.blinks_count = 0
        self.is_full = False
        self.buffer.clear()
        self.times.clear()
        self.blinks.clear()

    def handle_blink(self, blink):
        if not self.is_full:
            print("AutoBlinkBuffer - Got blink before buffer is full. Ignore!")
            return
        blink_ts = blink.timestamp + (self.blink_from/self.sampling)
        blink_pos = self._get_times_index(blink.timestamp)
        #print("TS: "+str(blink_ts))
        #print("POS: "+str(blink_pos))
        if blink_pos < 0:
            return
        elif blink_pos >= self.whole_buf_len:
            # nie ma jeszcze nawet pierwszej probki
            #print(str(self.sampling*(blink_ts - self._get_times_last())))
            blink_count = self.ret_buf_len + int(self.sampling*(blink_ts - self._get_times_last()))
            blink_pos = self.whole_buf_len - self.ret_buf_len
        else:
            # gdzies w srodku
            blink_count = self.ret_buf_len - (self.whole_buf_len - blink_pos)
            if blink_count < 0:
                blink_count = 0
            blink_pos -= blink_count

        if not len(self.blinks) == 0:
            last = self.blinks[0]
            #print("LAST: "+str(last.count))
            blink_count -= self.blinks_count#last.count #get_last_blink()

        #print("count: "+str(blink_count))
        #print("pos: "+str(blink_pos))
        b = Blink(blink,blink_count, blink_pos)
        self.blinks.append(b)
        self.blinks_count += blink_count
        #[10, 15, 18, 22]

    def handle_sample_vect(self, sample_vector):
        for i in range(len(sample_vector.samples)):
            self.handle_sample(sample_vector.samples[i], sample_vector.samples[i].timestamp)

    def handle_sample(self, s, t):
        #print(str(s.channels[0])+" / "+str(t))
        self.buffer.add(s)
        self.times_sample.channels[0] = t
        self.times.add(self.times_sample)
        self.count += 1

        if not self.is_full:
            self.is_full = (self.count == self.whole_buf_len)
        else:
            if not len(self.blinks) == 0:
                #print("HAVE BLINKS"+str(len(self.blinks)))
                curr = self.blinks[0]
                curr.count -= 1
                self.blinks_count -= 1
                #print("COUNT "+str(curr.count))
                if curr.count <= 0:
                    curr = self.blinks.popleft()
                    d = self.buffer.get(curr.position, self.ret_buf_len)
                    self.ret_func(curr.blink, d)


    def _get_times_index(self, value):
        if self.is_full:
            last = self.whole_buf_len
        else:
            last = self.count
        vect = self.times.get(0, last)[0]
        ret = -1
        for i, v in enumerate(vect):
            if value < v:
                return ret
            ret = i
        return self.whole_buf_len


    def _get_times_last(self):
        if self.is_full:
            last = self.whole_buf_len
        else:
            last = self.count
        return self.times.get(0, last)[0][last-1]
            
