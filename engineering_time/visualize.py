'''
This script offers different plotting functions for looking at the engineering data.
'''

__author__ = 'Taylor Hutchison'
__email__ = 'aibhleog@tamu.edu'
__version__ = 'Oct2019'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gd

def xyshift(df,rotcolor=True,savefig=True):
	elevations = list(set(df.el))
	rotpposns = list(set(df.rotpposn))

	# visualize the data
	plt.figure(figsize=(9,6))

	# plotting all measured xshifts and yshifts
	if rotcolor == True:
		plt.scatter(df.xshift,df.yshift,c=df.rotpposn,cmap='viridis',edgecolor='k',zorder=5)
	
		cbar = plt.colorbar()
		cbar.set_ticks(np.sort(rotpposns))
		plt.text(1.21,0.4,'rotpposn',rotation=270,transform=plt.gca().transAxes,fontsize=16)
	else:
		plt.scatter(df.xshift,df.yshift,edgecolor='k',zorder=5)

	plt.title('Reference frame: EL=5$^\mathrm{o}$ ROTPPOSN=0$^\mathrm{o}	$')
	plt.xlabel('(x$_0 -$ x) [pixels]')
	plt.ylabel('(y$_0 -$ y) [pixels]')

	plt.tight_layout()
	if savefig == True: plt.savefig('../plots-data/data_FCS/xyshift.png',dpi=300)
	else: plt.show()
	plt.close('all')


def xshift_rot(df,savefig=True):
	elevations = list(set(df.el))
	rotpposns = list(set(df.rotpposn))

	# visualize the data
	plt.figure(figsize=(9,6))
	plt.scatter(df.rotpposn,df.xshift,c=df.el,cmap='viridis',edgecolor='k',zorder=5)
	plt.gca().set_xticks(np.sort(rotpposns))

	cbar = plt.colorbar()
	cbar.set_ticks(np.sort(elevations))
	plt.text(1.16,0.4,'elevation',rotation=270,transform=plt.gca().transAxes,fontsize=16)

	plt.title('Reference frame: EL=5$^\mathrm{o}$ ROTPPOSN=0$^\mathrm{o}	$')
	plt.ylabel('(x$_0 -$ x) [pixels]')
	plt.xlabel('rotpposn [degrees]')

	plt.tight_layout()
	if savefig == True: plt.savefig('../plots-data/data_FCS/xshift_rot.png',dpi=300)
	else: plt.show()
	plt.close('all')

def yshift_rot(df,savefig=True):
	elevations = list(set(df.el))
	rotpposns = list(set(df.rotpposn))

	# visualize the data
	plt.figure(figsize=(9,6))
	plt.scatter(df.rotpposn,df.yshift,c=df.el,cmap='viridis',edgecolor='k',zorder=5)
	plt.gca().set_xticks(np.sort(rotpposns))

	cbar = plt.colorbar()
	cbar.set_ticks(np.sort(elevations))
	plt.text(1.16,0.4,'elevation',rotation=270,transform=plt.gca().transAxes,fontsize=16)

	plt.title('Reference frame: EL=5$^\mathrm{o}$ ROTPPOSN=0$^\mathrm{o}	$')
	plt.ylabel('(y$_0 -$ y) [pixels]')
	plt.xlabel('rotpposn [degrees]')

	plt.tight_layout()
	if savefig == True: plt.savefig('../plots-data/data_FCS/yshift_rot.png',dpi=300)
	else: plt.show()
	plt.close('all')

def xshift_el(df,savefig=True):
	elevations = list(set(df.el))
	rotpposns = list(set(df.rotpposn))

	# visualize the data
	plt.figure(figsize=(9,6))
	plt.scatter(df.el,df.xshift,c=df.rotpposn,cmap='viridis',edgecolor='k',zorder=5)
	plt.gca().set_xticks(np.sort(elevations))
	
	cbar = plt.colorbar()
	cbar.set_ticks(np.sort(rotpposns))
	plt.text(1.21,0.4,'rotpposn',rotation=270,transform=plt.gca().transAxes,fontsize=16)

	plt.title('Reference frame: EL=5$^\mathrm{o}$ ROTPPOSN=0$^\mathrm{o}	$')
	plt.ylabel('(x$_0 -$ x) [pixels]')
	plt.xlabel('elevation [degrees]')

	plt.tight_layout()
	if savefig == True: plt.savefig('../plots-data/data_FCS/xshift_el.png',dpi=300)
	else: plt.show()
	plt.close('all')

def yshift_el(df,savefig=True):
	elevations = list(set(df.el))
	rotpposns = list(set(df.rotpposn))

	# visualize the data
	plt.figure(figsize=(9,6))
	plt.scatter(df.el,df.yshift,c=df.rotpposn,cmap='viridis',edgecolor='k',zorder=5)
	plt.gca().set_xticks(np.sort(elevations))
	
	cbar = plt.colorbar()
	cbar.set_ticks(np.sort(rotpposns))
	plt.text(1.21,0.4,'rotpposn',rotation=270,transform=plt.gca().transAxes,fontsize=16)

	plt.title('Reference frame: EL=5$^\mathrm{o}$ ROTPPOSN=0$^\mathrm{o}	$')
	plt.ylabel('(y$_0 -$ y) [pixels]')
	plt.xlabel('elevation [degrees]')

	plt.tight_layout()
	if savefig == True: plt.savefig('../plots-data/data_FCS/yshift_el.png',dpi=300)
	else: plt.show()
	plt.close('all')








