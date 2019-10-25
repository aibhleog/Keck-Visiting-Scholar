'''
Module for measuring and displaying the seeing for a given mask.
The following methods exist in this module:

	get_seeing() -- takes a Drift() object and returns seeing
	                measurements for both offsets (assumes ABAB)
	seeing_map() -- given frame numbers and measured seeing,
	                returns a map of the seeing for both nods
	                as a function of frame number (assumes ABAB)

Future upgrades:
> changing seeing_map() to plot UTC vs seeing
> overlay airmass
'''

__author__ = 'Taylor Hutchison'
__email__ = 'aibhleog@tamu.edu'
__version__ = 'Oct2019'

import pandas as pd
import matplotlib.dates as md
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from pandas.plotting import register_matplotlib_converters
from drift import *
import matplotlib

register_matplotlib_converters()


# -------------------------------------------------------------------------- #

def make_colormap(cen,dmin,dmax,size):
	# coming up with a range that helps us figure out where the color is
	t = np.linspace(dmin,dmax,size)
	s = np.linspace(0,1,size)
	n = size*10

	x = cen/(dmax-dmin)-0.6
	print('x: %s, Min: %s, Max: %s\n'%(x,dmin,dmax))

	upper = plt.cm.Reds(np.linspace(0,0.6,n*round(x-0.01*x,2)))
	#focus = plt.cm.rainbow(np.ones(3)*x)
	lower = plt.cm.Blues(np.linspace(1,0,n*round(1-(x+0.01*x),2)))
	#colors = np.vstack((lower, focus, upper))
	colors = np.vstack((lower, upper))
	tmap = matplotlib.colors.LinearSegmentedColormap.from_list('taylor', colors)
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
# -------------------------------------------------------------------------- #


def get_seeing(drift_obj):
	'''
	Fits a gaussian to each raw frame's star and produces the 
	seeing measurements.
	
	INPUTS ---- home:   path to directory containing MOSFIRE data
	            drift_obj:  a drift_obj() object with defined variables
	
	RETURNS --- eight arrays (grouped 2 & 2 & 2 & 2) describing frame 
	            number, UTC, seeing, & airmass for each nod (assumes ABAB)
	'''
	nod_A, nod_B = drift_obj.split_dither()
	utc_A, utc_B = drift_obj.get_UTC(nod_A), drift_obj.get_UTC(nod_B)
	air_A, air_B = drift_obj.get_airmass(nod_A), drift_obj.get_airmass(nod_B)

	# ------------- measuring the fits ------------- #
	# ---------------------------------------------- #
	cen_A, A_A, sig_A, num_A = drift_obj.fit_all(nod_A)   
	cen_B, A_B, sig_B, num_B = drift_obj.fit_all(nod_B)   
	# ---------------------------------------------- #

	# takes the sigma and uses FWHM = sigma*2.35 (approximation)
	# to get the FWHM value, then converts pixels to " by the 
	# MOSFIRE conversion of 0.18 "/pixel
	seeing_A = np.asarray(sig_A) * 2.35 * 0.18 # "/pixel
	seeing_B = np.asarray(sig_B) * 2.35 * 0.18 # "/pixel
	return [num_A, num_B], [utc_A, utc_B], [seeing_A, seeing_B], [air_A, air_B]


def seeing_map(time,seeing,airmass,drift_obj,savefig=False,see=True):
	'''
	Produces a seeing map as a function of frame.

	INPUTS ---- frame:      2XN array, ex. [nod_A,nod_B]
			    seeing:     2XN array, ex. [seeing_A,seeing_B]

	RETURNS --- plot of the seeing map
	'''
	from scipy.signal import medfilt 

	# Formatting UTC   
	time[0] = [dt.strptime(i,'%H:%M:%S.%f') for i in time[0]]
	time[1] = [dt.strptime(i,'%H:%M:%S.%f') for i in time[1]]
	#print(time[0][0],time[1][0])


	# modifying colormap
	cen, dmin, dmax = 2,1,3.5
	x = cen / (dmax-dmin)
	tmap = make_colormap(cen,dmin,dmax,len(seeing[0]))
	norm = FixPointNormalize(fixme=cen,fixhere=x,vmin=dmin,vmax=2.5)


	# plotting information
	plt.figure(figsize=(11,6))
	plt.gca().xaxis.set_major_formatter(md.DateFormatter('%H:%M'))

	# running median
	smoothed1 = medfilt(seeing[0],15)
	smoothed2 = medfilt(seeing[1],15)
	smoothed = np.hstack((np.stack((smoothed1,smoothed2),axis=1)))
	total_time = np.hstack((np.stack((time[0],time[1]),axis=1)))

	plt.scatter(time[0],seeing[0],c=airmass[0],cmap=tmap,norm=norm,edgecolor='k',s=60,label='Nod A')
	plt.scatter(time[1],seeing[1],c=airmass[0],cmap=tmap,norm=norm,edgecolor='k',marker='^',s=60,label='Nod B')
	#plt.plot(total_time,smoothed)

	plt.text(0.975,0.94,'Mask: %s'%(drift_obj.mask),ha='right',\
			 transform=plt.gca().transAxes,fontsize=15)
	plt.text(0.975,0.88,'Date: %s'%(drift_obj.date),ha='right',\
			 transform=plt.gca().transAxes,fontsize=16)

	# colorbar
	cbar = plt.colorbar(bbox_to_anchor=(1,0.3))
	cbar.set_label('Airmass',rotation=270,labelpad=18)
	cbar.ax.invert_yaxis()

	plt.legend(loc=2)
	plt.xlabel('UTC')
	plt.ylabel('seeing ["]')
	plt.ylim(0.4,2)
	plt.xlim(time[0][0],time[1][-1])

	plt.tight_layout()
	if savefig == True: 
		plt.savefig(f'plots-data/seeing/seeing_map_{drift_obj.date}_{drift_obj.mask}.pdf')
	if see == True: plt.show()
	plt.close('all')
