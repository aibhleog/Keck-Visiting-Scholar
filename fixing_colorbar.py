'''
This code is just used to make the custom colorbars for the seeing and drift mapping plots.
'''

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

def elevation_cmap(cen,dmin,dmax,size):
	'''
	Returns the colormap that we want for the elevation colorbars.
	'''
	# coming up with a range that helps us figure out where the color is
	t = np.linspace(dmin,dmax,size)
	s = np.linspace(0,1,size)
	n = size*10

	x = cen/(dmax-dmin) # helps in centering the zeropoint
	#print('x: %s, Min: %s, Max: %s\n'%(x,dmin,dmax))

	lower = plt.cm.Reds(np.linspace(0.6,0,int(n*round(x-0.01*x,2))))
	upper = plt.cm.Blues(np.linspace(0,1,int(n*round(1-(x+0.01*x),2))))
	colors = np.vstack((lower, upper))
	tmap = matplotlib.colors.LinearSegmentedColormap.from_list('elevation', colors)
	return tmap


def airmass_cmap(cen,dmin,dmax,size):
	'''
	Returns the colormap that we want for the airmass colorbar.
	'''
	# coming up with a range that helps us figure out where the color is
	t = np.linspace(dmin,dmax,size)
	s = np.linspace(0,1,size)
	n = size*10

	x = cen/(dmax-dmin)-0.6 # helps in centering the zeropoint
	#print('x: %s, Min: %s, Max: %s\n'%(x,dmin,dmax))

	upper = plt.cm.Reds(np.linspace(0,0.6,int(n*round(x-0.01*x,2))))
	lower = plt.cm.Blues(np.linspace(1,0,int(n*round(1-(x+0.01*x),2))))
	colors = np.vstack((lower, upper))
	tmap = matplotlib.colors.LinearSegmentedColormap.from_list('airmass', colors)
	return tmap


class FixPointNormalize(matplotlib.colors.Normalize):
	""" 
	Inspired by https://stackoverflow.com/questions/20144529/shifted-colorbar-matplotlib
	Subclassing Normalize to obtain a colormap with a fixpoint 
	somewhere in the middle of the colormap.

	This may be useful for a `terrain` map, to set the "sea level" 
	to a color in the blue/turquise range as shown in example:
	https://stackoverflow.com/questions/40895021/python-equivalent-for-matlabs-demcmap-elevation-appropriate-colormap
	"""
	def __init__(self, vmin=None, vmax=None, fixme=5, fixhere=0.26, clip=False):
		# fixme is the fix point of the colormap (in data units)
	    self.fixme = fixme
	    # fixhere is the color value in the range [0,1] that should represent fixme
	    self.fixhere = fixhere
	    matplotlib.colors.Normalize.__init__(self, vmin, vmax, clip)

	def __call__(self, value, clip=None):
	    x, y = [self.vmin, self.fixme, self.vmax], [0, self.fixhere, 1]
	    return np.ma.masked_array(np.interp(value, x, y)) 
