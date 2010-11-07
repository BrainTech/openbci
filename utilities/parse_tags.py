#!/usr/bin/env python

import tags_file_reader
import struct
import numpy as np
import pylab
import sys
from matplotlib import pyplot as plt


def filter(d,f,window):
    data = abs(np.fft.rfft(d))
    j = len(data)
    #print "len data ", len(data), "len(d) ",len(d)
    for i in range(j):
        if (i >= 30 * window) or (i <=  2 * window) or (i == 28 * window):
            data[i] = 0.
       # if (i < len(d) - (f * window)) and (i>len(d)/2):
       #     data[i] = 0.
    t = np.arange(27)
    #pylab.plot(data)
    #pylab.show()
    plt.plot(t,data[:27])
    plt.show()
    data = np.fft.irfft(data)
    return data


def max_index(d):
    j = 0
    mx = d[0]
    mx_i = j
    for j in range(len(d)):
        if (d[j] > mx):
            mx = d[j]
            mx_i = j
    return mx_i

def max_power(d, f, window):
    #data = numpy.fft.rfft(data)
    d2 = abs(np.fft.rfft(d))
    d2 = [x*x for x in d2]
    t = np.arange(len(d2))
    plt.plot(t,d2)
    d3 = []
    for i in f:
        d3.append(d2[int(i) * window])
    
    #return f[max_index(d3)]
    t = np.arange(4)
    plt.plot(t,d3)
#    data = np.fft.rfft(d)
    plt.show()


def draw_spectrum(d):
    d2 = abs(np.fft.rfft(d))
#    d2 = [x*x for x in d2]
    pylab.plot(d2)
    pylab.show()

tags_f = open(sys.argv[1] + ".obci.tags")
t_reader = tags_file_reader.TagsFileReader(sys.argv[1] +".obci.tags")
t_reader.start_tags_reading()
tag = t_reader.get_next_tag()
tags = []
ok = True
f = open(sys.argv[1] + ".tagi", 'w')
while ok:
    tag = t_reader.get_next_tag()
    if tag == None:
        ok = False
    #print tag['name']
    else:
        if tag['name'] in ['experiment_update', 'sound', 'start_experiment']:
            #print tag['desc']['screen'], " ", tag['start_timestamp']
            tags.append(tag)
	    f.write(tag['name'] + " " + str(tag['start_timestamp']) +  " " + str(tag['end_timestamp']) + '\n') 
		#+ " " + tag['desc']['screen'] + '\n')


