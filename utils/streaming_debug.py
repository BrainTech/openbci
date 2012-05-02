#!/usr/bin/env python
#
# Author:
#      Mateusz Kruszynski <mateusz.kruszynski@gmail.com>

"""
Use to debug real-life streaming modules like:
- amplifier
- streamer
- filter
See signal_streamer_no_filter.py for sample use.
"""
import time
class Debug(object):
    def __init__(self, p_sampling, logger, per=1):
        """By now init externally given logger 
        (python standar logger object) and sampling."""
        self.num_of_samples = 0
        self.sampling = p_sampling
        self.logger = logger
        self.per = per
        
    def next_sample(self):
        """Called after every new sample received.
        Aftet sel.sampling sample print stats info."""
        if self.num_of_samples == 0:
            self.start_time = time.time()
            self.last_pack_first_sample_ts = time.time()

        pre_rest = self.num_of_samples % self.sampling 
        self.num_of_samples += self.per
        rest = self.num_of_samples % self.sampling 
        if pre_rest > rest:
            self.logger.info(''.join(
                    ["Time of last ",
                     str(self.sampling),
                     " samples / all avg: ",
                     str(time.time() - self.last_pack_first_sample_ts),
                     ' / ', 
                     str(self.sampling*(time.time() - self.start_time)/float(self.num_of_samples))]))
            self.last_pack_first_sample_ts = time.time()

    def next_sample_timestamp(self, sample_timestamp):
        if self.num_of_samples == 0:
            self.first_sample_timestamp = sample_timestamp
        self.num_of_samples += 1
        rest = self.num_of_samples % self.sampling 
        if rest == 0:
            self.logger.info(''.join(
                    ["Time of last ",
                     str(self.sampling),
                     " samples / all avg: ",
                     str(sample_timestamp - self.first_st_in_pack),
                     ' / ', 
                     str(self.sampling*(sample_timestamp - self.first_sample_timestamp)/float(self.num_of_samples))]))

        elif rest == 1:
            self.first_st_in_pack = sample_timestamp
        
