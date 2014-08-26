#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
>>> fs = 80.0

>>> from wii_analysis import *

>>> signal = test_signal()

>>> COP_path(signal)
(99.0, 99.0, 0.0)

>>> mean_velocity, velocity_AP, velocity_ML = mean_velocity(signal, fs)

>>> print("%.2f" % round(mean_velocity,2))
79.20

>>> print("%.2f" % round(velocity_AP,2))
0.00

>>> print("%.2f" % round(velocity_ML,2))
79.20

>>> RMS, RMS_ML, RMS_AP = RMS_AP_ML(signal)

>>> print("%.2f" % round(RMS,2))
28.87

>>> print("%.2f" % round(RMS_AP,2))
28.87

>>> print("%.2f" % round(RMS_ML,2))
0.00

>>> confidence_ellipse_area(signal)
0.0

>>> mean_sway, mean_sway_AP, mean_sway_ML = mean_COP_sway_AP_ML(signal)

>>> print("%.2f" % round(mean_sway,2))
25.00

>>> print("%.2f" % round(mean_sway_AP,2))
0.00

>>> print("%.2f" % round(mean_sway_ML,2))
25.00

>>> max_sway, max_sway_AP, max_sway_ML = max_sway_AP_ML(signal)

>>> print("%.2f" % round(max_sway,2))
49.50

>>> print("%.2f" % round(max_sway_AP,2))
0.00

>>> print("%.2f" % round(max_sway_ML,2))
49.50

>>> signal1 = test_signal1()

>>> get_percentages_values(signal1, fs, plot=False)
(50.0, 0.0, 0.0, 50.0)

>>> tripping_get_time(signal1, fs)
(1.0, 1.0)

>>> tripping_get_percentages(signal1, fs, plot=False)
(50.0, 50.0)

"""

def run():
	import doctest, sys
	res = doctest.testmod(sys.modules[__name__])
	if res.failed == 0:
		print("All tests succeeded!")

if __name__ == '__main__':
	run()

