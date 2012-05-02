# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
>>> from analysis.buffers import ring_buffer_numpy_channels as R

>>> r = R.RingBufferNumpyChannels(10, 5, False)

>>> for s in [get_sample(i, 5) for i in range(12)]: r.add(s)

>>> vals = r.get(3, 3)

>>> vals
array([[  5.00000000e+00,   6.00000000e+00,   7.00000000e+00],
       [  5.00000000e+01,   6.00000000e+01,   7.00000000e+01],
       [  5.00000000e+02,   6.00000000e+02,   7.00000000e+02],
       [  5.00000000e+03,   6.00000000e+03,   7.00000000e+03],
       [  5.00000000e+04,   6.00000000e+04,   7.00000000e+04]])


>>> vals[2, 1] = 1234.0

>>> vals
array([[  5.00000000e+00,   6.00000000e+00,   7.00000000e+00],
       [  5.00000000e+01,   6.00000000e+01,   7.00000000e+01],
       [  5.00000000e+02,   1.23400000e+03,   7.00000000e+02],
       [  5.00000000e+03,   6.00000000e+03,   7.00000000e+03],
       [  5.00000000e+04,   6.00000000e+04,   7.00000000e+04]])

>>> r.get(3, 3)
array([[  5.00000000e+00,   6.00000000e+00,   7.00000000e+00],
       [  5.00000000e+01,   6.00000000e+01,   7.00000000e+01],
       [  5.00000000e+02,   1.23400000e+03,   7.00000000e+02],
       [  5.00000000e+03,   6.00000000e+03,   7.00000000e+03],
       [  5.00000000e+04,   6.00000000e+04,   7.00000000e+04]])


>>> r = R.RingBufferNumpyChannels(10, 5, True)

>>> for s in [get_sample(i, 5) for i in range(19)]: r.add(s)

>>> vals = r.get(2, 2)

>>> vals
array([[  1.10000000e+01,   1.20000000e+01],
       [  1.10000000e+02,   1.20000000e+02],
       [  1.10000000e+03,   1.20000000e+03],
       [  1.10000000e+04,   1.20000000e+04],
       [  1.10000000e+05,   1.20000000e+05]])

"""


from configs import variables_pb2
def get_sample(v, ch):
    sample = variables_pb2.Sample()
    mult = 1
    for i in range(ch):
        sample.channels.append(float(v)*mult)
        mult*=10
    sample.timestamp = 10.0
    return sample


def run():
    import doctest, sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")

if __name__ == '__main__':
    run()
