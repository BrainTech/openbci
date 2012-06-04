#!/usr/bin/env python

import time

class SampleLogger(object):

    def __init__(self, log_interval=100):
        self.log_interval = log_interval
        self.samples_got = 0

        self.start_time = time.time()
        self.start_i = self.start_time
        self.end_i = self.start_time+1

        self.log = []

    def log_sample(self, timestamp=None):
        self.samples_got += 1
        if self.samples_got % self.log_interval == 0:
            self.end_i = time.time()
            self.log.append((self.end_i - self.start_i, self.samples_got, timestamp))
            self.start_i = self.end_i

    def mark_start(self):
        self.start_time = time.time()
        self.start_i = self.start_time

    def mark_end(self):
        self.end_i = time.time()

    def report(self, filename='log_py'):
        with open(filename, 'w') as f:
            f.write("Log interval: " + str(self.log_interval) + " samples\n")
            f.write("Partial rates:\n")
            for log in self.log:
                f.write(str(float(self.log_interval) / log[0]) + "  samples/s\n")
                f.write(str(log[1]) + " timestamp: " + str(log[2]) + "\n")

            f.write("Average:\n")
            f.write(str(float(self.samples_got) / (self.end_i - self.start_time)))

if __name__ == "__main__":
    SampleLogger().report()
