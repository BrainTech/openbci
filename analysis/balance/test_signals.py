#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
>>> fs = 80.0

>>> from wii_analysis import *

>>> sig = test_signal()

>>> COP_path(sig)
(99.0, 99.0, 0.0)

>>> max_sway_AP_MP(sig)
(1.0, 99.0)

>>> mean_velocity, velocity_AP, velocity_ML = mean_velocity(sig, fs)

>>> print("%.2f" % round(mean_velocity,2))
79.20

>>> print("%.2f" % round(velocity_AP,2))
0.00

>>> print("%.2f" % round(velocity_ML,2))
79.20

>>> RMS, RMS_ML, RMS_AP = RMS_AP_ML(sig)

>>> print("%.2f" % round(RMS,2))
9.95

>>> print("%.2f" % round(RMS_AP,2))
0.00

>>> print("%.2f" % round(RMS_ML,2))
9.95

"""

def run():
	import doctest, sys
	res = doctest.testmod(sys.modules[__name__])
	if res.failed == 0:
		print("All tests succeeded!")

if __name__ == '__main__':

	# from wii_analysis import *
	# signal = test_signal()
	# print RMS_AP_ML(signal)

	run()
