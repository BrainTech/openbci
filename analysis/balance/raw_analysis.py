# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

def test_signal(T=100, fs=1):
	dt = 1/fs
	x = np.arange(0, T, dt)
	y = np.ones(x.shape)
	return np.vstack((x,y))

def plot_graph(ax, title, x, y, xlabel, ylabel):
	ax.set_title(title)
	ax.plot(x, y)
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)

def plot_COP(signal, fs):
	""" Plots real values of COP positions: COPx(time), COPy(time) and COPy(COPx)
	Input:

	signal 	-- 2 dim array 		-- x,y values
	fs 		-- float			-- sampling frequency """

	time = np.arange(0,signal.shape[1]*1/fs,1/fs)
	f = plt.figure(figsize=(16,12))
	ax_x = f.add_subplot(221)
	plot_graph(ax_x, 'COPx position', time, signal[0], 
					 'time [s]', 'position COPx [cm]')
	# ax_x.set_xlim(0,30)
	ax_y = f.add_subplot(223)
	plot_graph(ax_y, 'COPy position', time, signal[1], 
					 'time [s]', 'position COPy [cm]')
	# ax_y.set_xlim(0,30)
	ax_xy = f.add_subplot(122)
	plot_graph(ax_xy, 'COP position', signal[0][:int(fs*30)], 
					 signal[1][:int(fs*30)], 'position COPx [cm]', 
					 'position COPy [cm]')
	f.canvas.draw()
	#f.savefig(str(file_name)+'.png')

def calculate_distance(position_1, position_2):
	""" Returns distance between two points or 1-dim and 2-dim vectors
	input:
	position1 -- int or 1-dim or 2-dim matrix
	position2 -- int or 1-dim or 2-dim matrix
	position1 and position2 must have the same dimension
	"""

	distance = position_2 - position_1
	
	try:
		return (distance[0]**2+distance[1]**2)**0.5
	except IndexError:
		return np.abs(distance)

def max_sway_AP_MP(signal):
	""" Returns maximal sway values for mediolateral (x) and anterioposterior (y) directions
	Input: 
	signal  --  2-dim array with shape (channel, samples) 
				(on the index 0 - samples from channel x, on index 1 - samples from channel y) 
	Output: 
	max_AP   	--  float
	max_ML  	--  float
	"""

	max_AP = max(signal[1,:])
	max_ML = max(signal[0,:])

	return max_AP, max_ML

def COP_path(signal):
	""" Returns total length of the COP path
	Input: 
	signal  --  2-dim array with shape (channel, samples) 
				(on the index 0 - samples from channel x, on index 1 - samples from channel y) 
	Output: 
	cop   	--  float
	cop_x  	--  float
	cop_y  	--  float
	"""

	cop = sum([calculate_distance(signal[:,index], signal[:, index+1]) for index in xrange(signal.shape[1]-1)])
	cop_x = sum([calculate_distance(signal[0,index], signal[0, index+1]) for index in xrange(signal.shape[1]-1)])
	cop_y = sum([calculate_distance(signal[1,index], signal[1, index+1]) for index in xrange(signal.shape[1]-1)])
	return cop, cop_x, cop_y

def RMS_AP_ML(signal):
	""" Returns Root Mean Square (RMS) values in medio-lateral and anterio-posterior directions"""

	RMS = np.sqrt(np.sum(np.array([calculate_distance(signal[:,index], signal[:, index+1]) for index in xrange(signal.shape[1]-1)])**2))
	RMS_ML = np.sqrt(np.sum(np.array([calculate_distance(signal[0,index], signal[0, index+1]) for index in xrange(signal.shape[1]-1)])**2))
	RMS_AP = np.sqrt(np.sum(np.array([calculate_distance(signal[1,index], signal[1, index+1]) for index in xrange(signal.shape[1]-1)])**2))
	return RMS, RMS_ML, RMS_AP

def confidence_ellipse_area():
	""" Returns area of the 95 perc. confidence ellipse"""
	return area

def mean_velocity(signal, fs):
	""" Returns average velocity of the COP, in ML and AP directions"""

	cop, cop_x, cop_y = COP_path(signal)
	mean_velocity = cop/(signal.shape[1]/fs)
	velocity_AP = cop_y/(signal.shape[1]/fs)
	velocity_ML = cop_x/(signal.shape[1]/fs)
	return mean_velocity, velocity_AP, velocity_ML

def reaction_time():
	""" Returns reaction time (2 standard deviations from baseline rest period till start signal)"""
	return rt

def triangles_area():
	""" Returns sway area (AREA-SW), which estimates the area enclosed by the COP path per unit of time. 
	This measure is approximated by summing the area of the triangles formed by two consecutive points 
	on the COP path and the mean COP """
	return area_sw

def mean_angle():
	""" Returns mean sway angle """
	return angle

def mean_COP_distance():
	""" Returns mean value of COP distance from the center point (0,0) """
	return cop_dist