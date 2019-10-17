'''
This file describes the class Drift(), which takes raw MOSFIRE data and
structures it such that it can be used to track drift and measure the seeing
as a function of frame (i.e., time).
'''

__author__ = 'Taylor Hutchison'
__email__ = 'aibhleog@tamu.edu'
__version__ = 'Oct2019'

import numpy as np
import matplotlib.pyplot as plt
import astropy.io.fits as fits
from scipy.interpolate import interp1d
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as PathEffects
from scipy.optimize import curve_fit
from datetime import datetime as dt
from astropy.stats import sigma_clip
import image_registration as ir # github.com/keflavich/image_registration
import collapse_profile as coll # written by TAH
import pandas as pd
import shutil
import os

import sys
if sys.version_info[0] < 3:
    raise Exception('Must be using Python 3+')

print('This class assumes you are based in the directory directly ' +\
          'above the MOSFIRE data. If this is not true, add the beginning of ' +\
          'your path to the kwarg "home" for each function.',end='\n\n')

class Drift:
    '''
    This class measures the drift of a given MOSFIRE dataset,
    provided there is a star in the mask. Check the input parameters
    to see what is needed to run this script successfully.
    '''
    
    # INPUT PARAMETERS
    date = ''       # string date for directories, ex. 2018nov25
    mask = ''       # mask name, ex. UDS_MOSFIRE_J
    dither = 0.0    # the dither in " of the mask (currently assumes ABAB)
    band = ''       # MOSFIRE band; choose from Y, J, H, K
    home = ''       # path for the MOSFIRE data
    
    # information about the star in the mask
    row_start = 0   # the yvalue for the bottom of the star's slit
    row_end = 0     # the yvalue for the top of the star's slit
    col_start = 0   # the xvalue for the first column (avoid skylines please)
    col_end = 0     # the xvalue for the last column (avoid skylines please)
    
    # LIST OF RAW FRAMES FOR CHOSEN MASK
    # -- full list of frames
    def mask_frames(self):
        '''
        Returns the list of MOSFIRE raw frames that are targeting the mask
        of choice. Will make distinction between calibrations and on-sky data.
        '''
        path = self.home+'%s/'%self.date
        #print(path)
        
        # converts the mask name into the format for the file names
        mfile = dt.strptime(self.date,'%Y%b%d').strftime('%y%m%d')
        #print('m'+mfile)
        
        allfiles = np.asarray(os.listdir(path))
        #allfiles = allfiles[]
        mfiles = [f[:7] for f in allfiles] # fast way to ignore other files
        raw_frames = allfiles[np.asarray(mfiles) == 'm'+mfile]
        raw_frames = np.sort(raw_frames)
        
        mask_frames = []
        for f in raw_frames:
            #print(f)
            head = fits.getheader(path+f)
            try:
                if head['OBJECT'] == self.mask:
                    #print(f)
                    mask_frames.append(f)
            except KeyError: pass
        return mask_frames
    
    # -- splitting into both dithers
    def split_dither(self):
        '''
        Returns the list of MOSFIRE raw frames that are targeting the mask
        of choice, split into the two dithers.
        '''
        path = self.home+'%s/'%self.date
        mask_frames = self.mask_frames()
        
        nod_A, nod_B = [],[]
        for filename in mask_frames:
            head = fits.getheader(path+filename)
            if head['GRATMODE'] == 'spectroscopy': # removes alignment frames
                if head['YOFFSET'] == self.dither: nod_A.append(filename)
                elif head['YOFFSET'] == -self.dither: nod_B.append(filename)
                else: raise Exception('ABAB dither pattern not found.')
            else: pass
                
        print('Number of frames in nod A: %s, in nod B: %s'%(len(nod_A),len(nod_B)),end='\n\n')
        return nod_A, nod_B
    
    
    # FITTING MODEL TO STAR'S PROFILE
    def cut_out(self,filename):
        '''
        Creates the cutout for the star's 2D spectrum.
        
        NOTE: when the new code is implemented here (see collapse_profile.py), the 2D cutout
        returned will be used for the seeing map and the star drift tracker (like usual).
        HOWEVER, the "blank2D" things in the collapse_profile.py module will be used to run
        cross-correlations & return the shift of the mask.
        '''
        path = self.home+'%s/'%self.date  
        
        star_img = fits.getdata(path+filename)
        profile_2D = star_img[self.row_start:self.row_end,self.col_start:self.col_end].copy()
        
        # CLIPPING OUT COSMIC RAYS
        # --> the threshold is sigma=2 because the code runs on the 
        # --> rows of the 2D, where every value should be consistent
        # --> i.e., "spectrally"
        mask = sigma_clip(profile_2D,sigma=2,axis=1)
        profile_2D[mask.mask] = np.median(profile_2D)
        # replacing the cosmic ray pixels with the median
        
        return profile_2D
        
    def fit_model(self,filename):
        '''
        Creating the mask star's profile given a handful of columns to sum 
        over (to increase the S/N), this function fits this profile.
        
        NOTE: when the new code is implemented here (see collapse_profile.py), this function
        will have the skylines masked out and the whole thing will be collapsed.  Then, we
        won't need to specify the columns.
        
        INPUTS ---- filename:   str, name of raw MOSFIRE file to be read in
                    row_start:  int, the yvalue for the bottom of the star's slit
                    row_end:    int, the yvalue for the top of the star's slit
                    col_start:  int, the xvalue for the first column (no skylines please)
                    col_end:    int, the xvalue for the last column (no skylines please)
            
        RETURNS --- mean:       float, center pixel of profile
                    A:          float, value of counts at peak
                    sig:        float, standard deviation -- can get FWHM by ~2.35*sig

        '''
        path = self.home+'%s/'%self.date    
        
        def gauss(xaxis, mean, A, sig, B): 
            # simple gaussian fit
            return A * np.exp(-np.power(xaxis-mean, 2.)/(2*np.power(sig, 2.))) + B

        # -- reading in data for the star
        profile_2D = self.cut_out(filename)
        profile = np.sum(profile_2D,axis=1) # summing over a few columns to increase S/N

        # ---- fitting the profile of the star
        x = np.arange(len(profile))
        peak = profile.tolist().index(max(profile)) # index for spatial peak of emission
        #print(peak,end=',')
        popt, wavcov = curve_fit(gauss,x,profile,p0=[x[peak],profile[peak],4.,0.])

        mean, A, sig, B = popt
        return mean, A, sig
    
    def cross_correlations(self,reference,filename):
        '''
        Takes filenames of reference frame & another frame, reads in data, & calculates
        the shift of the second frame from the reference using cross-correlations.
        
        INPUTS ---- reference:      str, name of raw MOSFIRE file to use as ref.
                    filename:       str, name of raw MOSFIRE file to be read in
        
        RETURNS --- xshift,yshift:  (float,float), shift of frame relative to reference
        '''
        path = self.home+'%s/'%self.date
        ref_frame = fits.getdata(path+reference)
        raw_frame = fits.getdata(path+filename)
        
        # masking out rows with signal in both
        # default sigma clipping: upper_sig=2.5, lower_sig=5
        ref_frame = coll.return_blank2D(ref_frame)
        raw_frame = coll.return_blank2D(raw_frame)
        
        # running the cross-correlation
        xshift,yshift = ir.cross_correlation_shifts(ref_frame,raw_frame)
        return xshift,yshift # shift from ref_frame to raw_frame
                             # essentially tracks the drift of the slit
        
    
    def get_UTC(self,filename):
        '''
        Pulling UTC information for a given filename or multiple filenames.
        
        INPUTS ---- filename:   str, name of raw MOSFIRE file to be read in
        RETURNS --- utc_value:  string or array, UTC information for frames
        '''
        path = self.home+'%s/'%self.date
        
        try: len(filename); one = False # more than one file
        except TypeError: one = True
            
        if one == True:
            head = fits.getheader(path+filename)
            utc = head['utc']
        else:
            utc = []
            for i in range(len(filename)):
                head = fits.getheader(path+filename[i])
                utc.append(head['utc'])
                
        return utc
    
    
    # CONVENIENCE FUNCTIONS
    # retrieving the fit for an entire dataset
    def fit_all(self,frames):
        '''
        Runs the fitting function on a large number of frames.
        Returns the fit parameters and the frame numbers.
        '''
        all_centers, all_As, all_sigs, frame_number = [],[],[],[]
        for filename in frames:
            mean, A, sig = self.fit_model(filename)
            all_centers.append(mean)
            all_As.append(A)
            all_sigs.append(sig)
            frame_number.append(int(filename[-8:-5]))
    
        return all_centers, all_As, all_sigs, frame_number
    
    # plotting all of the profiles for inspection
    def show_me_all_profiles(self,frames):
        '''
        Given frames, makes the cutouts, collapses spectrally,
        and plots all of the profiles for inspection.
        '''
        path = self.home+'%s/'%self.date    

        # plotting the profiles
        plt.figure(figsize=(9,6))
        for filename in frames:
            # -- reading in data for the star
            profile_2D = self.cut_out(filename)
            profile = np.sum(profile_2D,axis=1)
            plt.plot(profile)
        
        plt.tight_layout()
        plt.show()
        plt.close('all')
    