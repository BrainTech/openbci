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

def wii_max_sway_AP_MP(x, y):
	""" Returns maximal sway values for medio-lateral and anterio-posterior directions

	Input:
	x 				-- array -- samples from x channel
	y 				-- array -- samples from y channel
	Output:
	max_sway 	--	float 
	max_AP   	--  float
	max_ML  	--  float
	"""

	return max_sway_AP_ML(np.vstack((x,y)))

def wii_COP_path(wbb_mgr, x, y, plot=False):
	""" Returns total length of the COP path

	Input:
	WBBReadManager 	-- WBBReadManager object
	x 				-- array -- samples from x channel
	y 				-- array -- samples from y channel
	plot 			-- bool  -- optional
	"""
	
	if plot:
		fs = float(wbb_mgr.mgr.get_param('sampling_frequency'))
		plot_COP(np.vstack((x,y)),fs)
	return COP_path(np.vstack((x,y)))

def wii_RMS_AP_ML(x, y):
	""" Returns Root Mean Square (RMS) values in medio-lateral and anterio-posterior directions"""

	return RMS_AP_ML(np.vstack((x,y)))

def wii_confidence_ellipse_area(x, y):
	""" Returns area of the 95 perc. confidence ellipse"""

	return confidence_ellipse_area(np.vstack((x,y)))

def wii_mean_velocity(wbb_mgr, x, y):
	""" Returns average velocity of the COP, in ML and AP directions

	Input:
	WBBReadManager 	-- WBBReadManager object
	x 				-- array -- samples from x channel
	y 				-- array -- samples from y channel
	"""

	fs = float(wbb_mgr.mgr.get_param('sampling_frequency'))
	return mean_velocity(np.vstack((x,y)), fs)

# def wii_reaction_time():
# 	""" Returns reaction time (2 standard deviations from baseline rest period till start signal)"""
# 	return rt

# def wii_triangles_area():
# 	""" Returns sway area (AREA-SW), which estimates the area enclosed by the COP path per unit of time. 
# 	This measure is approximated by summing the area of the triangles formed by two consecutive points 
# 	on the COP path and the mean COP """
# 	return area_sw

# def wii_mean_angle():
# 	""" Returns mean sway angle """
# 	return angle

def wii_mean_COP_sway_AP_ML(x, y):
	""" Returns mean value of COP sway from the center point (0,0).

	Input:
	x 				-- array -- samples from x channel
	y 				-- array -- samples from y channel
	"""

	return mean_COP_sway_AP_ML(np.vstack((x,y)))

def wii_get_percentages_values(wbb_mgr, x, y, plot=False):
	"""
	Returns percentages of being on each of four parts of board.

	Input:
	WBBReadManager 	-- WBBReadManager object
	x 				-- array -- samples from x channel
	y 				-- array -- samples from y channel
	plot 			-- bool  -- optional

	Output:
		top_right 		-- float
		top_left		-- float
		bottom_right	-- float
		bottom_left		-- float
	"""

	fs = float(wbb_mgr.mgr.get_param('sampling_frequency'))
	return get_percentages_values(np.vstack((x,y)), fs, plot=plot)