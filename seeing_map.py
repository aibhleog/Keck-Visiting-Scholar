'''
Module for measuring and displaying the seeing for a given mask.
The following methods exist in this module:

	get_seeing() -- takes a Drift() object and returns seeing
		            measurements for both offsets (assumes ABAB)
	seeing_map() -- given frame numbers and measured seeing,
		            returns a map of the seeing for both nods
		            as a function of frame number (assumes ABAB)

Future upgrades:
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
from fixing_colorbar import *
import matplotlib

register_matplotlib_converters()

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
	tmap = airmass_cmap(cen,dmin,dmax,len(seeing[0]))
	norm = FixPointNormalize(fixme=cen,fixhere=x,vmin=dmin,vmax=2.5)

	# plotting information
	plt.figure(figsize=(11,6))
	plt.gca().xaxis.set_major_formatter(md.DateFormatter('%H:%M'))

	plt.scatter(time[0],seeing[0],c=airmass[0],cmap=tmap,norm=norm,edgecolor='k',s=60,label='Nod A')
	plt.scatter(time[1],seeing[1],c=airmass[1],cmap=tmap,norm=norm,edgecolor='k',marker='^',s=60,label='Nod B')

	plt.text(0.975,0.94,'Mask: %s'%(drift_obj.mask),ha='right',\
			 transform=plt.gca().transAxes,fontsize=15)
	plt.text(0.975,0.88,'Date: %s'%(drift_obj.date),ha='right',\
			 transform=plt.gca().transAxes,fontsize=16)

	
	# colorbar
	cbar = plt.colorbar()#(bbox_to_anchor=(1,0.3))
	cbar.set_label('Airmass',rotation=270,labelpad=18)
	cbar.ax.invert_yaxis()

	plt.legend(loc=2)
	plt.xlabel('UTC')
	plt.ylabel('seeing ["]')
	plt.ylim(0.3,2)
	plt.xlim(time[0][0],time[1][-1])

	plt.tight_layout()
	if savefig == True: 
		plt.savefig(f'plots-data/seeing/seeing_map_{drift_obj.date}_{drift_obj.mask}.pdf')
	if see == True: plt.show()
	plt.close('all')
