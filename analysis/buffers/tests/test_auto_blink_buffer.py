# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
>>> from analysis.buffers import auto_blink_buffer as R

>>> per, ch, sm = (4, 3, 20)

>>> ts_step = 1/float(sm)

>>> f = print_bufs

>>> b = R.AutoBlinkBuffer(0, 5, ch, sm, f, 'NUMPY_CHANNELS', False)

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))#1-4

>>> b.handle_blink(B(time.time()))
AutoBlinkBuffer - Got blink before buffer is full. Ignore!

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))

>>> b.handle_blink(B(time.time()))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step)) #17-20

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step)) 
FUNC
[[   18.    19.    20.    21.    22.]
 [  180.   190.   200.   210.   220.]
 [ 1800.  1900.  2000.  2100.  2200.]]


>>> b.handle_blink(B(time.time()))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step)) #25-28

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))
FUNC
[[   26.    27.    28.    29.    30.]
 [  260.   270.   280.   290.   300.]
 [ 2600.  2700.  2800.  2900.  3000.]]


>>> b.handle_blink(B(time.time()))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step)) #33-36

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))
FUNC
[[   34.    35.    36.    37.    38.]
 [  340.   350.   360.   370.   380.]
 [ 3400.  3500.  3600.  3700.  3800.]]






>>> zero_count()

>>> b = R.AutoBlinkBuffer(0, 10, ch, sm, f, 'NUMPY_CHANNELS', False)

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))#1-4

>>> b.handle_blink(B(time.time()))
AutoBlinkBuffer - Got blink before buffer is full. Ignore!

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step)) #17-20

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step)) 

>>> b.handle_blink(B(time.time()))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step)) #25-28

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))

>>> b.handle_blink(B(time.time()))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step)) #33-36
FUNC
[[   26.    27.    28.    29.    30.    31.    32.    33.    34.    35.]
 [  260.   270.   280.   290.   300.   310.   320.   330.   340.   350.]
 [ 2600.  2700.  2800.  2900.  3000.  3100.  3200.  3300.  3400.  3500.]]


>>> b.handle_blink(B(time.time()))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))
FUNC
[[   34.    35.    36.    37.    38.    39.    40.    41.    42.    43.]
 [  340.   350.   360.   370.   380.   390.   400.   410.   420.   430.]
 [ 3400.  3500.  3600.  3700.  3800.  3900.  4000.  4100.  4200.  4300.]]

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))
FUNC
[[   38.    39.    40.    41.    42.    43.    44.    45.    46.    47.]
 [  380.   390.   400.   410.   420.   430.   440.   450.   460.   470.]
 [ 3800.  3900.  4000.  4100.  4200.  4300.  4400.  4500.  4600.  4700.]]


>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))




>>> zero_count()

>>> b = R.AutoBlinkBuffer(0, 10, ch, sm, f, 'NUMPY_CHANNELS', False)

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))#1-4

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step)) #17-20

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step)) 

>>> t = time.time()

>>> b.handle_blink(B(t-ts_step*6))

>>> b.handle_blink(B(t-ts_step*5))

>>> b.handle_blink(B(t-ts_step*4))

>>> b.handle_blink(B(t-ts_step*3))

>>> b.handle_blink(B(t-ts_step*2))

>>> b.handle_blink(B(t-ts_step*1))

>>> b.handle_blink(B(t))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step)) #25-28

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step)) #33-36

>>> b.handle_blink(B(time.time()))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))

>>> b.handle_blink(B(time.time()))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))#41-44

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))

>>> b.handle_sample_vect(get_sample_vector(per, ch, ts_step))


"""
class B(object):
    def __init__(self, t):
        self.timestamp = t

def zero_count():
    global COUNT
    COUNT = 0

from obci_configs import variables_pb2
import time
COUNT = 0

def get_sample_vector(per, ch_num, ts_step):
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
        #print(samp.channels[0])
        samp.timestamp = time.time()
        time.sleep(ts_step)
    return sample_vector


def print_bufs(blink, bufs):
    print("FUNC")
    print bufs

def run():
    import doctest, sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")

if __name__ == '__main__':
    run()
