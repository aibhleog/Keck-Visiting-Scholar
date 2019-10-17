'''
This module takes a 2D array (raw FITS image from MOSFIRE) and does the following:
    --  collapses it spatially, searches for gaussian signal above a certain threshold, 
        THEN can do one of the following:
        1.  return 2D slit where star is located (assumed to be highest S/N spatially)
        2.  return 2D array where star & other high S/N rows are masked out
        
This module will be used for both the seeing & drift tracking of the star *as well as* the drift of the slit itself.  If drift is measured in both the star & slit, likely an internal FCS problem; if just the star, likely a guider flexure or differential atmospheric refraction (DAR) problem.

    CURRENT TROUBLESHOOTING NEEDED:
    -------------------------------
    There's a version of "drift.py" that lives one directory up (in "drift/").
    I was trying to implement this into the class structure, but I was having problems.
    I added in a count variable to the class object that would only let this be run once
    for the return_star() function.
    --> Currently have a skyline issue. Need to figure out how to mask out the skylines
        otherwise the collasping won't work.
    
'''

__author__ = 'Taylor Hutchison'
__email__ = 'aibhleog@tamu.edu'
__version__ = 'Oct2019'

import pandas as pd
from drift import *

import warnings
warnings.filterwarnings("ignore")

def collapse_2D(arr):
    '''
    This function takes a 2D array (assuming raw MOSFIRE image) and collapses it spatially. Can be used later for more complex functions.
    
    INPUTS ---- arr:            NxN array, assumed to be raw MOSFIRE FITS
    RETURNS --- nansum(arr):    1XN array, collapsed FITS clipped of cosmics
    '''
    
    # CLIPPING OUT COSMIC RAYS
    # --> the threshold is sigma=2 because the code runs on the 
    # --> rows of the 2D, where every value should be consistent
    # --> i.e., "spectrally"
    mask = sigma_clip(arr,sigma=2,axis=1)
    arr[mask.mask] = np.nan
    return np.nansum(arr,axis=1)


# NEED TO MASK OUT SKYLINES
def return_star(arr,sigma=5,see=False):
    '''
    This function takes a collapsed raw image (spatially), finds the star, and returns a 2D slice with the star's profile clearly defined. 
    
    INPUTS ---- arr:        NxN array, assumed to be collapsed FITS
                see:        bool, to see the clipping results
                sigma:      int, set high so only star is found
    
    RETURNS --- y1,y2:      (int,int), rows encompassing the star's signal
                            widened to include the other dither
    '''
    spatial = collapse_2D(arr) # getting spatial profile of mask
    med,std = np.median(spatial),np.std(spatial)
    mask = spatial < med - std*1.5 # cutting out the spaces
    spatial[mask] = np.nan                                  # between the slits (low values)

    # masking out everything but the location of the star
    # expected to be high S/N so sigma = 5 is currently used.
    mask = sigma_clip(spatial,sigma=5)
    star = spatial.copy()
    star[~mask.mask] = np.nan
    
    if see == True:
        plt.figure(figsize=(11,5))
        plt.plot(spatial,label='full profile')      # full spatial profile
        plt.plot(star,label='location of star')     # masked out to show just star
        
        plt.legend()
        plt.tight_layout()
        plt.show()
        plt.close('all')
        
    # for now, just return range of rows around the star
    # by providing 10 pixels on either side of the peak emission
    peak = star.tolist().index(np.nanmax(star))
    return peak-27,peak+27  # the rows encompassing the star's slit
                            # widened to include the other dither

    
def make_blank(arr,upper_sigma=3,lower_sigma=5,see=False):
    '''
    This function takes a collapsed raw image (spatially) and masks out regions that have a discernible signal, so that only the slit gaps, skylines, and noise remain.
    
    INPUTS ---- arr:            NxN array, assumed to be collapsed FITS
                see:            bool, to see the clipping results
                upper_sigma:    int, upper limit for finding signal
                lower_sigma:    int, lower limit set large so slit gaps
                                aren't clipped from the FITS profile
                                
    RETURNS --- blank:          1xN array, index of spatial profile where the
                                bad rows (i.e., signal) have been set to NaN 
    '''
    spatial = collapse_2D(arr) # getting spatial profile of mask
    
    # masking out all real signals, but want to keep slit gaps
    mask = sigma_clip(spatial,sigma_lower=lower_sigma,sigma_upper=upper_sigma)
    blank = spatial.copy()
    blank[mask.mask] = np.nan # blocks out the big signals
    
    # running through index values for those flagged -- setting indx +/- 5 to
    # NaNs as well to be safe that the full signal profiles are covered
    indx = np.arange(len(blank))
    indx = indx[np.isnan(blank)] # returns the index of the NaNs
    for i in indx:
        blank[i-5:i+5] = np.nan
    
    if see == True:
        plt.figure(figsize=(11,5))
        plt.plot(spatial,label='full profile')      # full spatial profile
        plt.plot(blank,label='masked out signals') # masked out to show just star
        
        plt.legend()
        plt.tight_layout()
        plt.show()
        plt.close('all')
    
    return blank


def return_blank2D(arr,upper_sigma=2.5,lower_sigma=5,see=False):
    '''
    This function runs the make_blank() function and applies the output to mask the 2D such that only the slit gaps, skylines, and noise remain.
    
    INPUTS ---- arr:            NxN array, assumed to be collapsed FITS
                see:            bool, to see the clipping results
                upper_sigma:    int, upper limit for finding signal
                lower_sigma:    int, lower limit set large so slit gaps
                                aren't clipped from the FITS profile
                                
    RETURNS --- blank2D:        NxN array, index of spatial profile where the
                                bad rows (i.e., signal) have been set to NaN 
    '''
    spatial = make_blank(arr,upper_sigma=upper_sigma,lower_sigma=lower_sigma,see=see)
    indx = np.arange(len(spatial))
    mask = indx[np.isnan(spatial)] # points out where NaNs are
    
    blank2D = arr.copy()
    blank2D[mask] = np.nan
    
    return blank2D # FITS image with those points masked out