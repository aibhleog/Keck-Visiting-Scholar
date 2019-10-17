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

def get_star_drift(drift_obj):
    '''
    Finds the peak of the emission (spatially) for a star in a mask, 
    measures the drift by comparing every raw frame to the spatial
    location of the first frame.
    
    INPUTS ---- home:       path to directory containing MOSFIRE data
                drift_obj:  a Drift() object with defined variables
    
    RETURNS --- four arrays (grouped 2 & 2) describing frame number & drift  
                for each nod (assumes ABAB)
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
    
    INPUTS ---- home:       path to directory containing MOSFIRE data
                drift_obj:  a Drift() object with defined variables
    
    RETURNS --- four arrays (grouped 2 & 2) describing frame number & drift  
                for each nod (assumes ABAB)
    '''
    # -- getting list of files for both dithers
    nod_A, nod_B = drift_obj.split_dither()
    ref_A, ref_B = nod_A[0],nod_B[0] # reference frame is 1st frame
    
    # calculating for first nod
    shifts_A = [[],[]]
    for i in range(len(nod_A)):
        x,y = drift_obj.cross_correlations(ref_A,nod_A[i])
        shifts_A[0].append(x)
        shifts_A[1].append(y)
        
    # calculating for second nod
    shifts_B = [[],[]]
    for i in range(len(nod_B)):
        x,y = drift_obj.cross_correlations(ref_B,nod_B[i])
        shifts_B[0].append(x)
        shifts_B[1].append(y)
        
    # the calculated shifts (from reference frame) for both nods
    return shifts_A, shifts_B
        

def star_drift_map(frame,offset,drift_obj,savefig=False,see=True):
    '''
    Produces a star drift map as a function of frame.
    
    INPUTS ---- frame:      2XN array, ex. [nod_A,nod_B]
                drift:      2XN array, ex. [off_A,off_B]
                drift_obj:  a Drift() object with defined variables
    
    RETURNS --- plot of the star drift map
    '''
    plt.figure(figsize=(9,6))
    plt.scatter(frame[0],offset[0],edgecolor='k',s=60,label='Nod A')
    plt.scatter(frame[1],offset[1],edgecolor='k',marker='^',s=60,label='Nod B')

    plt.text(0.025,0.05,'Mask: %s'%(drift_obj.mask),\
             transform=plt.gca().transAxes,fontsize=15)
    plt.text(0.025,0.1,'Date: %s'%(drift_obj.date),\
             transform=plt.gca().transAxes,fontsize=16)

    plt.legend(loc=2)
    plt.xlabel('frame number')
    plt.ylabel('$y_0 - y$ ["]')
    if min(offset[0]) < -0.2 and min(offset[0]) > -2:
        plt.ylim(min(offset[0])+min(offset[0])*0.3,0.4)
    else:
        plt.ylim(-0.2,0.4)

    plt.tight_layout()
    if savefig == True: 
        plt.savefig(f'plots-data/star_drift/star_drift_map_{drift_obj.date}_{drift_obj.mask}.pdf')
    if see == True: plt.show()
    plt.close()
    

def slit_drift_map(frame,drift_obj,savefig=False,see=True):
    '''
    Produces a slit drift map as a function of frame. Uses the 
    
    INPUTS ---- frame:      2XN array, ex. [nod_A,nod_B]
                drift_obj:  a Drift() object with defined variables
    
    RETURNS --- plot of the slit drift map
    '''
    plt.figure(figsize=(9,6))
    plt.scatter(frame[0],offset[0],edgecolor='k',s=60,label='Nod A')
    plt.scatter(frame[1],offset[1],edgecolor='k',marker='^',s=60,label='Nod B')

    plt.text(0.025,0.05,'Mask: %s'%(drift_obj.mask),\
             transform=plt.gca().transAxes,fontsize=15)
    plt.text(0.025,0.1,'Date: %s'%(drift_obj.date),\
             transform=plt.gca().transAxes,fontsize=16)

    plt.legend(loc=2)
    plt.xlabel('frame number')
    plt.ylabel('$y_0 - y$ ["]')
    if min(offset[0]) < -0.2 and min(offset[0]) > -2:
        plt.ylim(min(offset[0])+min(offset[0])*0.3,0.4)
    else:
        plt.ylim(-0.2,0.4)

    plt.tight_layout()
    if savefig == True: 
        plt.savefig(f'plots-data/slit_drift/slit_drift_map_{drift_obj.date}_{drift_obj.mask}.pdf')
    if see == True: plt.show()
    plt.close()

    