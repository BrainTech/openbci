#!/usr/bin/env python
# -*- coding: utf-8 -*-

class AutoBlinkBuffer(object):
    def __init__(self, from_sample, samples_count, every, num_of_channels, ret_func, ret_format, copy_on_ret):
        
        assert(samples_count > 0)
        assert(from_sample > 0)
        assert(every > 0)
        assert(num_of_channels > 0)
        assert(ret_format in ['PROTOBUF_SAMPLES', 'NUMPY_CHANNELS'])

        self.ret_func = ret_func
        self.every = every

        self.whole_buf_len = from_sample
        self.ret_buf_len = samples_count

        self.count = 0
        self.is_full = False

        if ret_format == 'PROTOBUF_SAMPLES':
            import ring_buffer_protobuf_samples
            self.buffer = ring_buffer_protobuf_samples.RingBufferProtobufSamples(from_sample, num_of_channels, copy_on_ret)
        elif ret_format == 'NUMPY_CHANNELS':
            import ring_buffer_numpy_channels
            self.buffer = ring_buffer_numpy_channels.RingBufferNumpyChannels(from_sample, num_of_channels, copy_on_ret)

    def __init__(self):
        self.ret_buf_len = 1024
        self.blink_from = -128
        self.sampling = float(1024)
        self.curr_blink = None
        self.curr_blink_ts = None
        self.count = 0
        self.is_full = False
        self.whole_buf_len = (self.ret_buf_len + abs(self.blink_from))*2 #2 in case blink comes not in real-time


    def clear(self):
        self.count = 0
        self.is_full = False
        self.buffer.clear()
        self.times.clear()

    def handle_blink(blink):
        blink_ts = blink.timestamp + (self.blink_from/self.sampling)
        blink_pos = self.times.get_index(blink.timestamp)
        if blink_pos < 0:
            pass # nie ma już sygnału
        elif blink_pos >= self.whole_buf_len:
            # nie ma jeszcze nawet pierwszej probki
            blink_count = self.ret_buf_len + self.sampling*(blink_ts + self.times.last()) #
            blink_pos = self.whole_buf_len - self.ret_buf_len
        else:
            # gdzies w srodku
            blink_count = self.ret_buf_len - (self.whole_buf_len - blink_pos)
            if blink_count < 0:
                blink_count = 0
            blink_pos -= blink_count

        if not self.blinks.empty():
            blink_count -= self.blinks.get_last_blink().count

        self.blinks.add((blink,blink_count, blink_pos))
        #[10, 15, 18, 22]

    def handle_sample_vect(self, sample_vector):
        for i in range(len(sample_vector.samples)):
            self.handle_sample(sample_vector.samples[i], sample_vector.timestamp)

    def handle_sample(self, s, t):
        self.buffer.add(s)
        self.times.add(t)
        self.count += 1

        if not self.is_full:
            self.is_full = (self.count == self.whole_buf_len)
        else:
            if not self.blinks.empty():
                curr = self.blinks.peep()
                curr.count -= 1
                if curr.count <= 0:
                    curr = self.blinks.pop()
                    d = self.buffer.get(curr.position, self.ret_buf_len)
                    self.ret_func(curr.blink, d)
