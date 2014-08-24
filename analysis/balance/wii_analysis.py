# -*- coding: utf-8 -*-
from raw_analysis import *
from wii_read_manager import *
import numpy as np
import matplotlib.pyplot as plt


""" Module to compute posturographic measures (most after Prieto T., "Measures of Postural Steadiness: 
	Differences Between Healthy Young and Elderly Adults", IEEE Transactions of biomedical engineering, 
	vol. 43, no. 9, 1996)

	- max_sway_AP_MP()
	- COP_path()
	- RMS_AP_ML()
	- confidence_ellipse_area()
	- mean_velocity()
	- reaction_time()
	- triangles_area()
	- mean_angle()
	- mean_COP_distance()
"""

def wii_max_sway_AP_MP():
	""" Returns maximal sway values for medio-lateral and anterio-posterior directions"""
	return max_AP, max_ML

def wii_COP_path(wbb_mgr, x, y, plot=False):
	""" Returns total length of the COP path"""
	
	cop = COP_path(np.vstack((x,y)))
	if plot:
		fs = float(wbb_mgr.mgr.get_param('sampling_frequency'))
		plot_COP(np.vstack((x,y)),fs)
	return cop

def wii_RMS_AP_ML():
	""" Returns Root Mean Square (RMS) values in medio-lateral and anterio-posterior directions"""
	return RMS_ML, RMS_AP

def wii_confidence_ellipse_area():
	""" Returns area of the 95 perc. confidence ellipse"""
	return area

def wii_mean_velocity():
	""" Returns average velocity of the COP, in ML and AP directions"""
	return mean_velocity, velocity_AP, velocity_ML

def wii_reaction_time():
	""" Returns reaction time (2 standard deviations from baseline rest period till start signal)"""
	return rt

def wii_triangles_area():
	""" Returns sway area (AREA-SW), which estimates the area enclosed by the COP path per unit of time. 
	This measure is approximated by summing the area of the triangles formed by two consecutive points 
	on the COP path and the mean COP """
	return area_sw

def wii_mean_angle():
	""" Returns mean sway angle """
	return angle

def wii_mean_COP_distance():
	""" Returns mean value of COP distance from the center point (0,0) """
	return cop_dist