'''
This code describes the current FCS model used by the MOSFIRE instrument.  Described by Nick Konidaris and Ryan Trainer (see "mosfire_fcs_model.pdf" in the MOSFIRE_information/ folder).

In short, the code can do two functions:
    1) provide pixel shifts based upon instrument "attitude"
    2) return piston values for tip/tilt corrections based on pixel shifts
'''

__author__ = 'Taylor Hutchison'
__email__ = 'aibhleog@tamu.edu'
__version__ = 'Oct2019'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import matplotlib.gridspec as gd
import matplotlib.patheffects as PathEffects

# reading in the data
df = pd.read_csv('../MOSFIRE_information/fcs_model_parameters.txt',\
                 index_col=0,delimiter='\s+') # parameter names are index

def flexure_comp(PA,Z,band):
    '''
    This code returns the pixels shifts given an instrument "attitude".
    
    INPUTS ---- PA:     float, rotation of instrument
                Z:      float, elevation
                band:   string, filter used for data
                
    RETURNS --- xshift: float, pixel shift in x-direction
                yshift: float, pixel shift in y-direction
    '''
    
    if band == 'Y' or band == 'J': filt = 'YJ'
    elif band == 'H' or band == 'K': filt = 'HK'
    else: filt = 'Mirror'
        
    a, y02, x02 = df.loc['a',filt], df.loc['y02',filt], df.loc['x02',filt]
    ph, k, beta = df.loc['ph',filt], df.loc['k',filt], df.loc['beta',filt]
    centerx, centery = df.loc['centerx',filt], df.loc['centery',filt]
    
    amp = a*np.sin(Z)
    Yc = y02*(1-np.cos(Z))
    Xc = x02*(1-np.cos(Z))
    
    deltaX = Xc + amp*np.cos(PA+ph)*np.sin(beta) - amp*k*np.sin(PA+ph)*np.cos(beta)
    deltaY = Yc + amp*np.cos(PA+ph)*np.cos(beta) + amp*k*np.sin(PA+ph)*np.sin(beta)
    
    xshift = deltaX - centerx
    yshift = deltaY - centery
    return xshift, yshift # units of pixels

def tip_tilt_corrections(PA,Z,band):
    '''
    This code returns piston values for tip/tilt corrections based on pixel shifts.
    
    INPUTS ---- PA:     float, rotation of instrument
                Z:      float, elevation
                band:   string, filter used for data
                
    RETURNS --- thetax: float, tip correction
                thetay: float, tilt correction
    '''
    if band == 'Y' or band == 'J': filt = 'YJ'
    elif band == 'H' or band == 'K': filt = 'HK'
    else: filt = 'Mirror'
        
    xshift,yshift = flexure_comp(PA,Z,band)
    xscale, yscale = df.loc['xscale',filt], df.loc['yscale',filt]
    anamorph = df.loc['anamorph',filt]
    
    thetax = -1*yshift*yscale
    thetay = -1*xshift*xscale*anamorph
    return thetax,thetay # units of urad