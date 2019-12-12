'''
Module for measuring and displaying the drift for a given mask.
The following methods exist in this module:

    get_drift() --- takes a Drift() object and returns drift
                    measurements for both offsets (assumes ABAB)
    drift_map() --- given frame numbers and measured offsets,
                    returns a map of the drift for both nods
                    as a function of frame number (assumes ABAB)

Future upgrades:
> changing drift_map() to plot UTC vs drift
> overlay elevation
'''

__author__ = 'Taylor Hutchison'
__email__ = 'aibhleog@tamu.edu'
__version__ = 'Oct2019'

import pandas as pd
from drift import *
from fixing_colorbar import *

def get_star_drift(drift_obj):
    '''
    Finds the peak of the emission (spatially) for a star in a mask, 
    measures the drift by comparing every raw frame to the spatial
    location of the first frame.
    
    INPUTS ---- drift_obj:  a Drift() object with defined variables
    
    RETURNS --- four arrays (grouped 2 & 2) describing frame number &  
                drift for each nod (assumes ABAB)
    '''
    # -- getting list of files for both dithers
    nod_A, nod_B = drift_obj.split_dither()

    # ------------- measuring the fits ------------- #
    # ---------------------------------------------- #
    cen_A, A_A, sig_A, num_A = drift_obj.fit_all(nod_A)   
    cen_B, A_B, sig_B, num_B = drift_obj.fit_all(nod_B)   
    # ---------------------------------------------- #

    off_A = (cen_A[0]-cen_A) * 0.18 # "/pixel
    off_B = (cen_B[0]-cen_B) * 0.18 # "/pixel
    return [num_A, num_B], [off_A, off_B]


def get_slit_drift(drift_obj):
    '''
    Takes raw FITS data and masks out the rows of signal, then runs a
    comparison with a masked reference frame to calculate the x,y shift.
    Used to track the slit drift (can be different than the star drift).
    
    INPUTS ---- drift_obj:  a Drift() object with defined variables
    
    RETURNS --- four arrays (grouped 2 & 2) describing frame number &  
                shift for each nod (assumes ABAB)
    '''
    # -- getting list of files for both dithers
    nod_A, nod_B = drift_obj.split_dither()
    ref_A, ref_B = nod_A[0],nod_B[0] # reference frame is 1st frame
    print(ref_A,ref_B)
    
    # calculating for first nod
    shifts_A = [[],[]]
    framenum_A = []
    print('Nod A:')
    #for i in range(len(nod_A)):
    i = 0
    while i < len(nod_A):
        print('A:',i)
        x,y = drift_obj.cross_correlations(ref_A,nod_A[i])
        shifts_A[0].append(x)
        shifts_A[1].append(y)
        framenum_A.append(int(nod_A[i][-8:-5]))
        #if len(nod_A) < 25: i += 1
        #else: i += 5 # in case there are a lot of frames
        i += 1
        
    print()
    
    # calculating for second nod
    shifts_B = [[],[]]
    framenum_B = []
    print('Nod B:')
    #for i in range(len(nod_B)):
    i = 0
    while i < len(nod_B):
        print('B:',i)
        x,y = drift_obj.cross_correlations(ref_B,nod_B[i])
        shifts_B[0].append(x)
        shifts_B[1].append(y)
        framenum_B.append(int(nod_B[i][-8:-5]))
        #if len(nod_B) < 25: i += 1
        #else: i += 5
        i += 1
        
    # the calculated shifts (from reference frame) for both nods
    return [framenum_A,shifts_A], [framenum_B,shifts_B]
        

def drift_map(frame,offset,drift_obj,star=True,savefig=False,see=True):
	'''
	Produces a star or slit drift map as a function of frame.
	
	INPUTS ---- frame:      2XN array, ex. [nod_A,nod_B]
	            offset:     2XN array, ex. [off_A,off_B]
	            drift_obj:  a Drift() object with defined variables
	            star:       bool, tracking star drift or slit drift?
	            savefig:    bool, save figure; default False
	            see:        bool, show() figure; default True
	
	RETURNS --- plot of the star drift map
	'''
	if star == True: title = 'Star Drift Map'
	else: title = 'Slit Drift Map'
	
	# making the list of files
	mfile = 'm'+dt.strptime(drift_obj.date,'%Y%b%d').strftime('%y%m%d') # start of the file names
	mfiles_A, mfiles_B = [mfile+f'_{fr:04d}.fits' for fr in frame[0]],[mfile+f'_{fr:04d}.fits' for fr in frame[1]]
	# getting the pa and el information
	pa_A, el_A = drift_obj.get_pa_el(mfiles_A)
	pa_B, el_B = drift_obj.get_pa_el(mfiles_B)

	# modifying colormap
	cen, dmin, dmax = 35,20,90
	x = cen / (dmax-dmin)
	tmap = elevation_cmap(35,20,90,len(offset[0]))
	norm = FixPointNormalize(fixme=35,fixhere=x,vmin=20,vmax=90)

	# making figure
	plt.figure(figsize=(11,6))
	plt.scatter(frame[0],offset[0],edgecolor='k',c=el_A,cmap=tmap,norm=norm,s=60,label='Nod A')
	plt.scatter(frame[1],offset[1],edgecolor='k',c=el_B,cmap=tmap,norm=norm,marker='^',s=60,label='Nod B')

	plt.text(0.025,0.05,'Mask: %s'%(drift_obj.mask),\
	         transform=plt.gca().transAxes,fontsize=15)
	plt.text(0.025,0.1,'Date: %s'%(drift_obj.date),\
	         transform=plt.gca().transAxes,fontsize=16)

	# colorbar
	cbar = plt.colorbar()
	cbar.set_label('Elevation [deg]',rotation=270,labelpad=18)
	
	plt.title(title,fontsize=16)
	plt.legend(loc=2)
	plt.xlabel('frame number')
	plt.ylabel('$y_0 - y$ ["]')
	if min(offset[0]) < -0.2 and min(offset[0]) > -2:
	    plt.ylim(min(offset[0])+min(offset[0])*0.3,0.4)
	else:
		plt.ylim(-0.2,0.4)

	plt.tight_layout()
	if savefig == True: 
	    if star == True:
	        plt.savefig(f'plots-data/star_drift/star_drift_map_{drift_obj.date}_{drift_obj.mask}.pdf')
	    else:
	        plt.savefig(f'plots-data/slit_drift/slit_drift_map_{drift_obj.date}_{drift_obj.mask}.pdf')
	if see == True: plt.show()
	plt.close()
