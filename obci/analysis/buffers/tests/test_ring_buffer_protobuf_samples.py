# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
>>> from openbci.online_analysis import ring_buffer_protobuf_samples as R

>>> r = R.RingBufferProtobufSamples(10, 5, False)

>>> for i in range(4): r.add(i)

>>> r.get(0, 10)
[0, 1, 2, 3, None, None, None, None, None, None]


>>> r = R.RingBufferProtobufSamples(10, 5, False)

>>> for i in range(12): r.add(i)

>>> r.get(0, 10)
[2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

>>> for i in range(12, 15): r.add(i)

>>> r.get(0, 10)
[5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

>>> r.get(3, 3)
[8, 9, 10]

>>> r = R.RingBufferProtobufSamples(10, 5, False)

>>> for s in [get_sample(i, 5) for i in range(12)]: r.add(s)

>>> vals = r.get(3, 3)

>>> [[i for i in s.channels] for s in vals]
[[5.0, 50.0, 500.0, 5000.0, 50000.0], [6.0, 60.0, 600.0, 6000.0, 60000.0], [7.0, 70.0, 700.0, 7000.0, 70000.0]]

>>> vals[1].channels[2] = 1234.0

>>> [[i for i in s.channels] for s in vals]
[[5.0, 50.0, 500.0, 5000.0, 50000.0], [6.0, 60.0, 1234.0, 6000.0, 60000.0], [7.0, 70.0, 700.0, 7000.0, 70000.0]]

>>> [[i for i in s.channels] for s in r.get(3, 3)]
[[5.0, 50.0, 500.0, 5000.0, 50000.0], [6.0, 60.0, 1234.0, 6000.0, 60000.0], [7.0, 70.0, 700.0, 7000.0, 70000.0]]


>>> r = R.RingBufferProtobufSamples(10, 5, True)

>>> for s in [get_sample(i, 5) for i in range(12)]: r.add(s)

>>> vals = r.get(3, 3)

>>> [[i for i in s.channels] for s in vals]
[[5.0, 50.0, 500.0, 5000.0, 50000.0], [6.0, 60.0, 600.0, 6000.0, 60000.0], [7.0, 70.0, 700.0, 7000.0, 70000.0]]

>>> vals[1].channels[2] = 1234.0

>>> [[i for i in s.channels] for s in vals]
[[5.0, 50.0, 500.0, 5000.0, 50000.0], [6.0, 60.0, 1234.0, 6000.0, 60000.0], [7.0, 70.0, 700.0, 7000.0, 70000.0]]

>>> [[i for i in s.channels] for s in r.get(3, 3)]
[[5.0, 50.0, 500.0, 5000.0, 50000.0], [6.0, 60.0, 600.0, 6000.0, 60000.0], [7.0, 70.0, 700.0, 7000.0, 70000.0]]


"""


import variables_pb2
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
