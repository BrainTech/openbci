# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
>>> from openbci.online_analysis import auto_ring_buffer as R

>>> per, ch = (4, 10)

>>> f = print_bufs

>>> b = R.AutoRingBuffer(10, 5, 5, ch, f, 'NUMPY_CHANNELS', False)

>>> v1 = get_sample_vector(per, ch, 1)

>>> v2 = get_sample_vector(per, ch, 10)

>>> v3 = get_sample_vector(per, ch, 100)

>>> v4 = get_sample_vector(per, ch, 1000)

>>> b.handle_sample_vect(v1)

>>> b.handle_sample_vect(v2)

>>> b.handle_sample_vect(v3)
FUNC
[[   1.    2.    3.    4.   10.]
 [   2.    3.    4.    5.   20.]
 [   3.    4.    5.    6.   30.]
 [   4.    5.    6.    7.   40.]
 [   5.    6.    7.    8.   50.]
 [   6.    7.    8.    9.   60.]
 [   7.    8.    9.   10.   70.]
 [   8.    9.   10.   11.   80.]
 [   9.   10.   11.   12.   90.]
 [  10.   11.   12.   13.  100.]]


>>> b.handle_sample_vect(v4)
FUNC
[[   11.    12.    13.   100.   101.]
 [   21.    22.    23.   200.   201.]
 [   31.    32.    33.   300.   301.]
 [   41.    42.    43.   400.   401.]
 [   51.    52.    53.   500.   501.]
 [   61.    62.    63.   600.   601.]
 [   71.    72.    73.   700.   701.]
 [   81.    82.    83.   800.   801.]
 [   91.    92.    93.   900.   901.]
 [  101.   102.   103.  1000.  1001.]]


>>> b = R.AutoRingBuffer(10, 3, 5, ch, f, 'NUMPY_CHANNELS', False)

>>> b.handle_sample_vect(v1)

>>> b.handle_sample_vect(v2)

>>> b.handle_sample_vect(v3)
FUNC
[[  1.   2.   3.]
 [  2.   3.   4.]
 [  3.   4.   5.]
 [  4.   5.   6.]
 [  5.   6.   7.]
 [  6.   7.   8.]
 [  7.   8.   9.]
 [  8.   9.  10.]
 [  9.  10.  11.]
 [ 10.  11.  12.]]


>>> b.handle_sample_vect(v4)
FUNC
[[  11.   12.   13.]
 [  21.   22.   23.]
 [  31.   32.   33.]
 [  41.   42.   43.]
 [  51.   52.   53.]
 [  61.   62.   63.]
 [  71.   72.   73.]
 [  81.   82.   83.]
 [  91.   92.   93.]
 [ 101.  102.  103.]]
 

"""

import variables_pb2
def get_sample_vector(per, ch, mult):
    sample_vector = variables_pb2.SampleVector()
    for x in range(per):
        samp = sample_vector.samples.add()
        for j in range(ch):
            samp.channels.append(float(j+1)*mult+x)
        samp.timestamp = 10.0
    return sample_vector

def print_bufs(bufs):
    print("FUNC")
    print bufs

def run():
    import doctest, sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")

if __name__ == '__main__':
    run()
