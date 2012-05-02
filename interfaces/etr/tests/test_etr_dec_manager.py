# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
>>> import etr_dec_manager as mgr

>>> mgr.TEST_MODE = True

>>> mgr.TEST_MODE_TIME = 20.0

>>> import  variables_pb2

>>> v = variables_pb2.Sample2D()

>>> m = mgr.EtrDecManager()

>>> m.get_requested_configs()
['ETR_BUFFER_SIZE', 'ETR_PUSH_FEED_COUNT', 'ETR_PUSH_DEC_COUNT', 'ETR_AREA_COUNT', 'ETR_DEC_TYPE', 'ETR_IGNORE_MISSED']

>>> cfg = {'ETR_DEC_TYPE':'COUNT', 'ETR_PUSH_DEC_COUNT':'20', 'ETR_PUSH_FEED_COUNT':'10', 'ETR_BUFFER_SIZE':'2.0', 'ETR_IGNORE_MISSED':'0', 'ETR_AREA_COUNT':'4'}

>>> m.set_configs(cfg)

>>> v.timestamp = 10.01

>>> m.area_pushed(-1, v)

>>> v.timestamp = 11.03

>>> m.area_pushed(-1, v)

>>> v.timestamp = 13.5

>>> m.area_pushed(-1, v)

>>> m.get_feedbacks()
(-1, [0.0, 0.0, 0.0, 0.0])




>>> cfg = {'ETR_DEC_TYPE':'COUNT', 'ETR_PUSH_DEC_COUNT':'5', 'ETR_PUSH_FEED_COUNT':'1', 'ETR_BUFFER_SIZE':'10.0', 'ETR_IGNORE_MISSED':'0', 'ETR_AREA_COUNT':'4'}

>>> m = mgr.EtrDecManager()

>>> m.set_configs(cfg)

>>> v.timestamp = 10.01

>>> m.area_pushed(-1, v)

>>> v.timestamp = 11.03

>>> m.area_pushed(-1, v)

>>> v.timestamp = 13.5

>>> m.area_pushed(-1, v)


>>> v.timestamp = 9.0

>>> m.area_pushed(1, v)

>>> v.timestamp = 15.0

>>> m.area_pushed(1, v)

>>> v.timestamp = 16.0

>>> m.area_pushed(1, v)

>>> v.timestamp = 17.0

>>> m.area_pushed(2, v)

>>> v.timestamp = 18.0

>>> m.area_pushed(2, v)

>>> v.timestamp = 19.0

>>> m.area_pushed(2, v)

>>> m.get_feedbacks()
(-1, [0.0, 0.25, 0.5, 0.0])

>>> v.timestamp = 19.1

>>> m.area_pushed(2, v)

>>> v.timestamp = 19.2

>>> m.area_pushed(2, v)

>>> m.get_feedbacks()
(2, [0.0, 0.25, 1.0, 0])





>>> cfg = {'ETR_DEC_TYPE':'FRACTION', 'ETR_PUSH_DEC_COUNT':'0.6', 'ETR_PUSH_FEED_COUNT':'0.2', 'ETR_BUFFER_SIZE':'10.0', 'ETR_IGNORE_MISSED':'0', 'ETR_AREA_COUNT':'4'}

>>> m = mgr.EtrDecManager()

>>> m.set_configs(cfg)

>>> v.timestamp = 10.01

>>> m.area_pushed(-1, v)

>>> v.timestamp = 11.03

>>> m.area_pushed(-1, v)

>>> v.timestamp = 13.5

>>> m.area_pushed(-1, v)


>>> v.timestamp = 9.0

>>> m.area_pushed(1, v)

>>> v.timestamp = 15.0

>>> m.area_pushed(1, v)

>>> v.timestamp = 16.0

>>> m.area_pushed(1, v)

>>> v.timestamp = 17.0

>>> m.area_pushed(2, v)

>>> v.timestamp = 18.0

>>> m.area_pushed(2, v)

>>> v.timestamp = 19.0

>>> m.area_pushed(2, v)

>>> m.get_feedbacks()
(-1, [0.0, 0.12499999999999999, 0.4375, 0.0])

>>> v.timestamp = 19.1

>>> m.area_pushed(2, v)

>>> v.timestamp = 19.2

>>> m.area_pushed(2, v)

>>> m.get_feedbacks()
(2, [0.0, 0.25, 1.0, 0])


"""



def run():
    import doctest, sys
    res = doctest.testmod(sys.modules[__name__])
    if res.failed == 0:
        print("All tests succeeded!")

if __name__ == '__main__':
    run()
