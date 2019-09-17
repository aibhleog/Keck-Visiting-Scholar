'''
NOTE:   Currently still under construction!
        This script reads in data ran from a script that does not exist in this
            repository.  If you would like access to this script, please email
            the author and provide an explanation for why you would need it.

This script reads in a list of MOSFIRE engineering data and runs cross-correlations 
between the first frame and the rest.  These data will be used to correct/update the 
internal flexure compensation system (FCS) for MOSFIRE.
'''

__author__ = 'Taylor Hutchison'
__email__ = 'aibhleog@tamu.edu'
__version__ = 'Sept2019'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits
import matplotlib.gridspec as gd
import image_registration as ir # github.com/keflavich/image_registration
import argparse

# reading input information
parser = argparse.ArgumentParser(description="Running cross-correlation on engineering data.",
			usage='cross-correlation.py ...',
			epilog='Contact Taylor Hutchison at aibhleog@tamu.edu with questions.')

parser.add_argument('-h','--home',help='Path to files.',required=True)
parser.add_argument('-d','--date',help='Date files were taken.',required=True)
args = parser.parse_args()


# reading in data
print('Reading in data.',end='\n\n')
home = args.home
date = args.date
files = np.loadtxt(home+date+'files.list',dtype='str')
df = pd.read_csv(home+date+'fcs_info.dat',delimiter='\s+')

d0 = fits.getdata(home+date+files[0])
d1 = fits.getdata(home+date+files[12])
x, y = 1100,1300
half

print('Starting the correlate2d() function.')
corr = ir.cross_correlation_shifts(d0,d1) # returns xshift, yshift


print('Looking at data')
# looking at it
plt.figure(figsize=(7,10))
gs = gd.GridSpec(1,2,wspace=0.05)

# first frame
ax0 = plt.subplot(gs[0])
ax0.imshow(d0,clim=(-300,300))
ax0.set_xticklabels([])
ax0.set_yticklabels([])

# second frame
ax1 = plt.subplot(gs[1])
ax1.imshow(d1,clim=(-300,300))
ax1.set_xticklabels([])
ax1.set_yticklabels([])


plt.tight_layout()
plt.savefig('test.png')
#plt.show()
plt.close()






