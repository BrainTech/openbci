#!/usr/bin/env python
# -*- coding: utf-8 -*-

class AutoRingBuffer(object):
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


    def handle_sample_vect(self, sample_vector):
        for i in range(len(sample_vector.samples)):
            self.handle_sample(sample_vector.samples[i])

    def handle_sample(self, s):
        self.buffer.add(s)
        self.count += 1
        if not self.is_full:
            if self.count == self.whole_buf_len:
                self.is_full = True
                self.count = self.count % self.every
                if self.count == 0:
                    self.count = self.every

        if self.is_full and self.count == self.every:
            d = self.buffer.get(0, self.ret_buf_len)
            self.ret_func(d)
            self.count = 0
            

