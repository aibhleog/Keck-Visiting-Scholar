import numpy as np
import matplotlib.pyplot as plt
import astropy.io.fits as fits
from scipy.interpolate import interp1d
import matplotlib.gridspec as gridspec
import matplotlib.patheffects as PathEffects
from scipy.optimize import curve_fit
from datetime import datetime as dt
from astropy.stats import sigma_clip
import pandas as pd
import shutil
import os

__version__ = '2019sep4'

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
    
    # information about the star in the mask
    row_start = 0   # the yvalue for the bottom of the star's slit
    row_end = 0     # the yvalue for the top of the star's slit
    col_start = 0   # the xvalue for the first column (avoid skylines please)
    col_end = 0     # the xvalue for the last column (avoid skylines please)
    
    
    # LIST OF RAW FRAMES FOR CHOSEN MASK
    # -- full list of frames
    def mask_frames(self,home=''):
        '''
        Returns the list of MOSFIRE raw frames that are targeting the mask
        of choice. Will make distinction between calibrations and on-sky data.
        '''
        path = home+'%s/'%self.date
        
        allfiles = np.asarray(os.listdir(path))
        ending = [f[-4:] for f in allfiles] # fast way to ignore other files
        raw_frames = allfiles[np.asarray(ending) == 'fits']
        raw_frames = np.sort(raw_frames)
        
        mask_frames = []
        for f in raw_frames:
            head = fits.getheader(path+f)
            if head['object'] == self.mask:
                mask_frames.append(f)
        return mask_frames
    
    # -- splitting into both dithers
    def split_dither(self,mask_frames,home=''):
        '''
        Returns the list of MOSFIRE raw frames that are targeting the mask
        of choice, split into the two dithers.
        '''
        path = home+'%s/'%self.date
        
        nod_A, nod_B = [],[]
        for filename in mask_frames:
            head = fits.getheader(path+filename)
            if head['gratmode'] == 'spectroscopy': # removes alignment frames
                if head['yoffset'] == self.dither: nod_A.append(filename)
                elif head['yoffset'] == -self.dither: nod_B.append(filename)
                else: raise Exception('ABAB dither pattern not found.')
            else: pass
                
        print('Number of frames in nod A: %s, in nod B: %s'%(len(nod_A),len(nod_B)),end='\n\n')
        return nod_A, nod_B
    
    
    # FITTING MODEL TO STAR'S PROFILE
    def cut_out(self,filename,home=''):
        '''
        Creates the cutout for the star's 2D spectrum.
        '''
        path = home+'%s/'%self.date  
        
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
        
    def fit_model(self,filename,home=''):
        '''
        Creating the mask star's profile given a handful of columns to sum 
        over (to increase the S/N), this function fits this profile.
        The input parameters required:

            filename:   str, name of raw MOSFIRE file to be read in
            row_start:  int, the yvalue for the bottom of the star's slit
            row_end:    int, the yvalue for the top of the star's slit
            col_start:  int, the xvalue for the first column (no skylines please)
            col_end:    int, the xvalue for the last column (no skylines please)
            
        Returns the fit paramters of the mask star:

            mean:       float, center pixel of profile
            A:          float, value of counts at peak
            sig:        float, standard deviation -- can get FWHM by ~2.35*sig

        '''
        path = home+'%s/'%self.date    
        
        def gauss(xaxis, mean, A, sig, B): 
            # simple gaussian fit
            return A * np.exp(-np.power(xaxis-mean, 2.)/(2*np.power(sig, 2.))) + B

        # -- reading in data for the star
        profile_2D = self.cut_out(filename,home=home)
        profile = np.sum(profile_2D,axis=1) # summing over a few columns to increase S/N

        # ---- fitting the profile of the star
        x = np.arange(len(profile))
        peak = profile.tolist().index(max(profile)) # index for spatial peak of emission
        #print(peak,end=',')
        popt, wavcov = curve_fit(gauss,x,profile,p0=[x[peak],profile[peak],4.,0.])

        mean, A, sig, B = popt
        return mean, A, sig
    
    # CONVENIENCE FUNCTIONS
    # retrieving the fit for an entire dataset
    def fit_all(self,frames,home=''):
        '''
        Runs the fitting function on a large number of frames.
        Returns the fit parameters and the frame numbers.
        '''
        all_centers, all_As, all_sigs, frame_number = [],[],[],[]
        for filename in frames:
            mean, A, sig = self.fit_model(filename,home=home)
            all_centers.append(mean)
            all_As.append(A)
            all_sigs.append(sig)
            frame_number.append(int(filename[-8:-5]))
    
        return all_centers, all_As, all_sigs, frame_number
    
    # plotting all of the profiles for inspection
    def show_me_all_profiles(self,frames,home=''):
        '''
        Given frames, makes the cutouts, collapses spectrally,
        and plots all of the profiles for inspection.
        '''
        path = home+'%s/'%self.date    

        # plotting the profiles
        plt.figure(figsize=(9,6))
        for filename in frames:
            # -- reading in data for the star
            profile_2D = self.cut_out(filename,home=home)
            profile = np.sum(profile_2D,axis=1)
            plt.plot(profile)
        
        plt.tight_layout()
        plt.show()
        plt.close('all')
    
    

# TESTING ON 2018DEC12 DATA for COSMOS
test = Drift()

test.date = '2018apr25'
test.mask = 'EGSMask1'
test.dither = 1.25
test.band = 'J'

test.row_start = 1729
test.row_end = 1766
test.col_start = 972
test.col_end = 982


# -- getting list of files for both dithers
#home = '/home/aibhleog/Desktop/observing/'
home = '/run/media/aibhleog/eve_lily/observing-keck2018/'
all_frames = test.mask_frames(home=home)
nod_A, nod_B = test.split_dither(all_frames,home=home)


# ------------- measuring the fits ------------- #
# ---------------------------------------------- #
mean, A, sig, num = test.fit_all(nod_A,home=home)   
df_A = pd.DataFrame({'frame':num,'cen':mean,'A':A,'sig':sig})

mean, A, sig, num = test.fit_all(nod_B,home=home)   
df_B = pd.DataFrame({'frame':num,'cen':mean,'A':A,'sig':sig})
# ---------------------------------------------- #

df_A['offset'] = (df_A.loc[0,'cen']-df_A.cen.values) * 0.18 # "/pixel
df_B['offset'] = (df_B.loc[0,'cen']-df_B.cen.values) * 0.18 # "/pixel
df_A['seeing'] = df_A.sig.values * 2.35 * 0.18 # "/pixel
df_B['seeing'] = df_B.sig.values * 2.35 * 0.18 # "/pixel


# LOOKING AT THE DATA

# -- OFFSET AS FUNCTION OF TIME (i.e., FRAME) -- #
# ---------------------------------------------- #
plt.figure(figsize=(9,6))
plt.scatter(df_A.frame,df_A.offset,edgecolor='k',s=60,label='Nod A')
plt.scatter(df_B.frame,df_B.offset,edgecolor='k',marker='^',s=60,label='Nod B')

plt.text(0.975,0.05,'Mask: %s'%(test.mask),ha='right',\
         transform=plt.gca().transAxes,fontsize=15)
plt.text(0.975,0.1,'Date: %s'%(test.date),ha='right',\
         transform=plt.gca().transAxes,fontsize=16)

plt.legend(loc=2)
plt.xlabel('frame number')
plt.ylabel('$y_0 - y$ ["]')
plt.ylim(-0.2,0.4)

plt.tight_layout()
plt.show()
plt.close()
# ============================================== #


# -- SEEING MAP AS FUNCTION OF TIME (i.e., FRAME) -- #
# -------------------------------------------------- #
plt.figure(figsize=(9,6))
plt.scatter(df_A.frame,df_A.seeing,edgecolor='k',s=60,label='Nod A')
plt.scatter(df_B.frame,df_B.seeing,edgecolor='k',marker='^',s=60,label='Nod B')

plt.text(0.975,0.92,'Mask: %s'%(test.mask),ha='right',\
         transform=plt.gca().transAxes,fontsize=15)
plt.text(0.975,0.88,'Date: %s'%(test.date),ha='right',\
         transform=plt.gca().transAxes,fontsize=16)

plt.legend(loc=2)
plt.xlabel('frame number')
plt.ylabel('seeing ["]')
plt.ylim(0.4,1.6)

plt.tight_layout()
plt.show()
plt.close()
# ================================================== #

test.show_me_all_profiles(np.concatenate((nod_A,nod_B)),home=home)