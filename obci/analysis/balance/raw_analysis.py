# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

def test_signal(T=100, fs=1):
	dt = 1/fs
	x = np.arange(0, T, dt)
	y = np.ones(x.shape)
	return np.vstack((x,y))

def test_signal1(T=16.0, fs=10.0):
	dt = 1/fs
	x = np.arange(-T/2, T/2, dt)
	y = np.arange(-T/2, T/2, dt)
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

def max_sway_AP_ML(signal):
	""" Returns maximal sway values for mediolateral (x) and anterioposterior (y) directions
	Input: 
	signal  --  2-dim array with shape (channel, samples) 
				(on the index 0 - samples from channel x, on index 1 - samples from channel y) 
	Output:
	max_sway 	--	float 
	max_AP   	--  float
	max_ML  	--  float
	"""

	resultant_distance = np.sqrt((signal[0]-np.mean(signal[0]))**2+(signal[1]-np.mean(signal[1]))**2)
	distance_AP = signal[1]-np.mean(signal[1])
	distance_ML = signal[0]-np.mean(signal[0])
	return max(resultant_distance), max(np.abs(distance_AP)), max(np.abs(distance_ML))

def mean_COP_sway_AP_ML(signal):
	""" Returns mean sway values for mediolateral (x) and anterioposterior (y) directions

	Input: 
	signal  --  2-dim array with shape (channel, samples) 
				(on the index 0 - samples from channel x, on index 1 - samples from channel y) 
	Output: 
	mean_sway 	--	float
	mean_AP   	--  float
	mean_ML  	--  float
	"""
	resultant_distance = np.sqrt((signal[0]-np.mean(signal[0]))**2+(signal[1]-np.mean(signal[1]))**2)
	distance_AP = signal[1]-np.mean(signal[1])
	distance_ML = signal[0]-np.mean(signal[0])
	return np.mean(resultant_distance), np.mean(np.abs(distance_AP)), np.mean(np.abs(distance_ML))

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

	resultant_distance = np.sqrt((signal[0]-np.mean(signal[0]))**2+(signal[1]-np.mean(signal[1]))**2)
	distance_AP = signal[1]-np.mean(signal[1])
	distance_ML = signal[0]-np.mean(signal[0])
	RMS = np.sqrt(1./signal.shape[1]*np.sum(resultant_distance**2))
	RMS_ML = np.sqrt(1./signal.shape[1]*np.sum(distance_ML**2))
	RMS_AP = np.sqrt(1./signal.shape[1]*np.sum(distance_AP**2))
	return RMS, RMS_AP, RMS_ML

def confidence_ellipse_area(signal):
	""" Returns area of the 95 perc. confidence ellipse"""

	s_AP = np.std(signal[1])
	s_ML = np.std(signal[0])
	s_AP_ML = 1./signal.shape[1]*np.sum((signal[0]-np.mean(signal[0]))*(signal[1]-np.mean(signal[1])))
	area = 2*np.pi*3.0*np.sqrt(s_AP**2*s_ML**2-s_AP_ML**2)
	return area

def mean_velocity(signal, fs):
	""" Returns average velocity of the COP, in ML and AP directions"""

	cop, cop_x, cop_y = COP_path(signal)
	mean_velocity = cop/(signal.shape[1]/fs)
	velocity_AP = cop_y/(signal.shape[1]/fs)
	velocity_ML = cop_x/(signal.shape[1]/fs)
	return mean_velocity, velocity_AP, velocity_ML

# def reaction_time():
# 	""" Returns reaction time (2 standard deviations from baseline rest period till start signal)"""
# 	return rt

# def triangles_area():
# 	""" Returns sway area (AREA-SW), which estimates the area enclosed by the COP path per unit of time. 
# 	This measure is approximated by summing the area of the triangles formed by two consecutive points 
# 	on the COP path and the mean COP """
# 	return area_sw

# def mean_angle():
# 	""" Returns mean sway angle """
# 	return angle

def get_percentages_being(signal, fs, grid=0.1, plot=True):
		"""Return how long person was on o field grig x grid (%)
		
		Input: 
		signal  --  2-dim array with shape (channel, samples) 
					(index 0 - samples from channel x, index 1 - samples from channel y) 
		grid    --  float 	-- default 0.1 - side of the field which was divided space 
		plot    --  bool 	-- default True)

		Output: 
		percentages_being   --  2-dim array (with shape (xedges - 1 , yedges - 1)) 
								with information how long subject was on board 
								field [xedges[n], xedges[n+1],yedges[n], yedges[n+1]]
		xedges              --  1-dim array with value of x_grid edges
		yedges              --  1-dim array with value of y_grid edges
		"""

		x_min = signal[0].min()
		x_max = signal[0].max()
		y_min = signal[1].min()
		y_max = signal[1].max()
		grid_x, grid_y = get_grid(grid, x_min, x_max, y_min, y_max)
		percentages_being, xedges, yedges = np.histogram2d(signal[0], signal[1], bins=[grid_x.shape[0], grid_y.shape[0]], range=[[x_min, x_max],[y_min, y_max]])
		percentages_being *= 1/fs
		percentages_being /= (signal.shape[1]*1/fs)
		percentages_being *= 100
		if plot:
			plot_percentages_being(grid, percentages_being, xedges, yedges, signal)
		plt.show()
		return percentages_being, xedges, yedges

def get_percentages_values(signal, fs, plot=True):
	"""
	Returns percentages of being on each of four parts of board.

	Input:
	signal 	-- 2-dim array with shape (channel, samples) 
			   (index 0 - samples from channel x, index 1 - samples from channel y)
	fs 		-- float -- sampling frequency

	Output:
		top_right 		-- float
		top_left		-- float
		bottom_right	-- float
		bottom_left		-- float
	"""

	p, xedges, yedges = get_percentages_being(signal, fs, plot=plot)
	top_right = 0
	top_left = 0
	bottom_right = 0
	bottom_left = 0
	for j,x in enumerate(xedges[1:-1]):
		for i,y in enumerate(yedges[1:-1]):
			if x > 0 and y > 0:
				top_right += p[j,i]
			elif x < 0 and y > 0:
				top_left += p[j,i]
			elif x < 0 and y < 0:
				bottom_left += p[j,i]
			elif x > 0 and y < 0:
				bottom_right += p[j,i]
	return top_right, top_left, bottom_right, bottom_left


def get_grid(grid, x_min, x_max, y_min, y_max):
	grid_y = np.arange(-22.5,22.5, grid)
	grid_x = np.arange(-13, 13, grid)
	index_min_y = np.searchsorted(grid_y, y_min)
	index_max_y = np.searchsorted(grid_y, y_max)
	index_min_x = np.searchsorted(grid_x, x_min)
	index_max_x = np.searchsorted(grid_x, x_max)
	return grid_x[index_min_x-1:index_max_x+1], grid_y[index_min_y-1:index_max_y+1]

def plot_percentages_being(grid, percentages_being, xedges, yedges, sig):
	fig = plt.figure()
	ax = fig.gca()
	ax.set_title('histogram with percentagles\nbegining in field {}cm x {}cm [time %].'.format(grid, grid))
	im = mpl.image.NonUniformImage(ax, interpolation='nearest')
	xcenters = xedges[:-1] + 0.5 * (xedges[1:] - xedges[:-1])
	ycenters = yedges[:-1] + 0.5 * (yedges[1:] - yedges[:-1])
	im.set_data(xcenters, ycenters, percentages_being.T)
	plt.colorbar(mappable=im, ax=ax)
	ax.images.append(im)  
	ax.set_xlim(xedges[0], xedges[-1])
	ax.set_ylim(yedges[0], yedges[-1])
	ax.set_aspect('equal')
	ax.set_xlabel('x [cm]')
	ax.set_ylabel('y [cm]')
	ax.plot(sig[0], sig[1], 'w')

def tripping_get_percentages(signal, fs, plot=False):
	top_right, top_left, bottom_right, bottom_left = get_percentages_values(signal, fs, plot=plot)
	return top_right+bottom_right, top_left+bottom_left

def tripping_get_time(signal, fs):
	right, left = tripping_get_percentages(signal, fs, plot=False)
	length = signal.shape[1]/fs
	return right/100.0*length, left/100.0*length
