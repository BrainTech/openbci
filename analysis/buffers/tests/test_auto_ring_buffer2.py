# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
>>> from openbci.online_analysis import auto_ring_buffer as R

>>> per, ch = (4, 3)

>>> f = print_bufs

>>> b = R.AutoRingBuffer(5, 5, 5, ch, f, 'NUMPY_CHANNELS', False)

>>> b.handle_sample_vect(get_sample_vector(per, ch))

>>> b.handle_sample_vect(get_sample_vector(per, ch))
FUNC
[[   1.    2.    3.    4.    5.]
 [  10.   20.   30.   40.   50.]
 [ 100.  200.  300.  400.  500.]]


>>> b.handle_sample_vect(get_sample_vector(per, ch))
FUNC
[[    6.     7.     8.     9.    10.]
 [   60.    70.    80.    90.   100.]
 [  600.   700.   800.   900.  1000.]]

>>> b.handle_sample_vect(get_sample_vector(per, ch))
FUNC
[[   11.    12.    13.    14.    15.]
 [  110.   120.   130.   140.   150.]
 [ 1100.  1200.  1300.  1400.  1500.]]

>>> b.handle_sample_vect(get_sample_vector(per, ch))
FUNC
[[   16.    17.    18.    19.    20.]
 [  160.   170.   180.   190.   200.]
 [ 1600.  1700.  1800.  1900.  2000.]]


>>> b = R.AutoRingBuffer(10, 5, 3, ch, f, 'NUMPY_CHANNELS', False)

>>> zero_count()

>>> b.handle_sample_vect(get_sample_vector(per, ch))

>>> b.handle_sample_vect(get_sample_vector(per, ch))

>>> b.handle_sample_vect(get_sample_vector(per, ch))
FUNC
[[   3.    4.    5.    6.    7.]
 [  30.   40.   50.   60.   70.]
 [ 300.  400.  500.  600.  700.]]

>>> b.handle_sample_vect(get_sample_vector(per, ch))
FUNC
[[    6.     7.     8.     9.    10.]
 [   60.    70.    80.    90.   100.]
 [  600.   700.   800.   900.  1000.]]

>>> b.handle_sample_vect(get_sample_vector(per, ch))
FUNC
[[    9.    10.    11.    12.    13.]
 [   90.   100.   110.   120.   130.]
 [  900.  1000.  1100.  1200.  1300.]]

>>> b.handle_sample_vect(get_sample_vector(per, ch))
FUNC
[[   12.    13.    14.    15.    16.]
 [  120.   130.   140.   150.   160.]
 [ 1200.  1300.  1400.  1500.  1600.]]
FUNC
[[   15.    16.    17.    18.    19.]
 [  150.   160.   170.   180.   190.]
 [ 1500.  1600.  1700.  1800.  1900.]]

>>> b.handle_sample_vect(get_sample_vector(per, ch))
FUNC
[[   18.    19.    20.    21.    22.]
 [  180.   190.   200.   210.   220.]
 [ 1800.  1900.  2000.  2100.  2200.]]


>>> b = R.AutoRingBuffer(10, 10, 2, ch, f, 'NUMPY_CHANNELS', False)

>>> zero_count()

>>> b.handle_sample_vect(get_sample_vector(per, ch))

>>> b.handle_sample_vect(get_sample_vector(per, ch))

>>> b.handle_sample_vect(get_sample_vector(per, ch))
FUNC
[[    1.     2.     3.     4.     5.     6.     7.     8.     9.    10.]
 [   10.    20.    30.    40.    50.    60.    70.    80.    90.   100.]
 [  100.   200.   300.   400.   500.   600.   700.   800.   900.  1000.]]
FUNC
[[    3.     4.     5.     6.     7.     8.     9.    10.    11.    12.]
 [   30.    40.    50.    60.    70.    80.    90.   100.   110.   120.]
 [  300.   400.   500.   600.   700.   800.   900.  1000.  1100.  1200.]]

>>> b.handle_sample_vect(get_sample_vector(per, ch))
FUNC
[[    5.     6.     7.     8.     9.    10.    11.    12.    13.    14.]
 [   50.    60.    70.    80.    90.   100.   110.   120.   130.   140.]
 [  500.   600.   700.   800.   900.  1000.  1100.  1200.  1300.  1400.]]
FUNC
[[    7.     8.     9.    10.    11.    12.    13.    14.    15.    16.]
 [   70.    80.    90.   100.   110.   120.   130.   140.   150.   160.]
 [  700.   800.   900.  1000.  1100.  1200.  1300.  1400.  1500.  1600.]]



>>> b = R.AutoRingBuffer(10, 3, 8, ch, f, 'NUMPY_CHANNELS', False)

>>> zero_count()

>>> b.handle_sample_vect(get_sample_vector(per, ch))

>>> b.handle_sample_vect(get_sample_vector(per, ch))

>>> b.handle_sample_vect(get_sample_vector(per, ch))

>>> b.handle_sample_vect(get_sample_vector(per, ch))
FUNC
[[   7.    8.    9.]
 [  70.   80.   90.]
 [ 700.  800.  900.]]

>>> b.handle_sample_vect(get_sample_vector(per, ch))

>>> b.handle_sample_vect(get_sample_vector(per, ch))
FUNC
[[   15.    16.    17.]
 [  150.   160.   170.]
 [ 1500.  1600.  1700.]]



"""



import variables_pb2
COUNT = 0

def zero_count():
    global COUNT
    COUNT = 0

def get_sample_vector(per, ch_num):
    """generate signal like:
    [ [1,2,3,4,5....
      [10,20,30,40,50...
      [100,200,300, ...
    ...
    ]
    """
    global COUNT
    sample_vector = variables_pb2.SampleVector()
    for x in range(per):
        COUNT += 1
        samp = sample_vector.samples.add()
        for j in range(ch_num):
            samp.channels.append((10**(j))*COUNT)
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
