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
__version__ = 'Sept2019'

import pandas as pd
from drift import *

def get_drift(drift_obj):
    '''
    Finds the peak of the emission (spatially) for a star in a mask, 
    measures the drift by comparing every raw frame to the spatial
    location of the first frame.
    
    INPUTS ---- home:   path to directory containing MOSFIRE data
                drift_obj:  a drift_obj() object with defined variables
    
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


def drift_map(frame,offset,drift_obj,saveit=False):
    '''
    Produces a drift map as a function of frame.
    
    INPUTS ---- frame:      2XN array, ex. [nod_A,nod_B]
                drift:      2XN array, ex. [off_A,off_B]
    
    RETURNS --- plot of the seeing map
    '''
    plt.figure(figsize=(9,6))
    plt.scatter(frame[0],offset[0],edgecolor='k',s=60,label='Nod A')
    plt.scatter(frame[1],offset[1],edgecolor='k',marker='^',s=60,label='Nod B')

    plt.text(0.975,0.05,'Mask: %s'%(drift_obj.mask),ha='right',\
             transform=plt.gca().transAxes,fontsize=15)
    plt.text(0.975,0.1,'Date: %s'%(drift_obj.date),ha='right',\
             transform=plt.gca().transAxes,fontsize=16)

    plt.legend(loc=2)
    plt.xlabel('frame number')
    plt.ylabel('$y_0 - y$ ["]')
    plt.ylim(-0.2,0.4)

    plt.tight_layout()
    if saveit == True: 
        plt.savefig(f'plots-data/seeing_map_{drift_obj.date}_{drift_obj.mask}.png')
    plt.show()
    plt.close()

    