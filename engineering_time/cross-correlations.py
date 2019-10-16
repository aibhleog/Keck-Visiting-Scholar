'''
NOTE:   Currently still under construction!
        This script reads in data ran from a script that does not exist in this
            repository.  If you would like access to this script, please email
            the author and provide an explanation for why you would need it.

Calculates the shift for every frame relative to some reference frame. From the source code:
"image_registration/cross_correlation_shifts.py"

	Examples
	--------
	>>> import numpy as np
	>>> im1 = np.zeros([10,10])
	>>> im2 = np.zeros([10,10])
	>>> im1[4,3] = 1
	>>> im2[5,5] = 1
	>>> import image_registration
	>>> xoff,yoff = image_registration.cross_correlation_shifts(im1,im2)
	>>> im1_aligned_to_im2 = np.roll(np.roll(im1,int(yoff),1),int(xoff),0)
	>>> assert (im1_aligned_to_im2-im2).sum() == 0

Reference frame: el=45, rotpposn=-90 (orientation for flats, also common among datasets)
'''

__author__ = 'Taylor Hutchison'
__email__ = 'aibhleog@tamu.edu'
__version__ = 'Oct2019'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits
import matplotlib.gridspec as gd
from datetime import datetime as dt
import image_registration as ir # github.com/keflavich/image_registration
import argparse

# reading input information
parser = argparse.ArgumentParser(description="Running cross-correlation on engineering data.",
			usage='cross-correlation.py ...',
			epilog='Contact Taylor Hutchison at aibhleog@tamu.edu with questions.')

parser.add_argument('-p','--path',help='Path to files.',required=True)
parser.add_argument('-o','--FCS',help='FCS on? (y/n)',required=True)
parser.add_argument('-b','--band',help='Band data were taken in. (J/H)',required=True)
args = parser.parse_args()

# reading in data
print('Reading in data.',end='\n\n')
home = args.path
band = args.band
fcs_set = args.FCS
assert fcs_set == 'y' or fcs_set == 'n', 'Need to specify y or n for "FCS on?".'

org_df = pd.read_csv('../KVS-data/engineering_fcs_info.dat',delimiter='\t')

# deciding if looking at FCS on or off
if fcs_set == 'y': FCS_on_off = 'On'
elif fcs_set == 'n': FCS_on_off = 'Off'
df = org_df.query(f'object == "Flexure Test FCS {FCS_on_off}" and band == "{band}"').copy()
df.reset_index(inplace=True,drop=True)


# -- reference frame -- #
if band == 'J' and FCS_on_off == 'Off': ref_el = 75
else: ref_el = 85
ref_df = df.query(f'el == {ref_el} and rotpposn == 0').copy()
ref_df.reset_index(inplace=True,drop=True) # making ref_df because there can be > 1 match
reference = ref_df.loc[0,'file']

# getting date info for reading in FITS image,
# to see how this works try line 82 with d = 'm130512_0001.fits'
d = ref_df.loc[0,'file']
date = dt.strptime(d[1:7],'%y%m%d').strftime('%Y%b%d').lower()
d0 = fits.getdata(home+date+'/'+reference)

# adding columns for xshift and yshift
df['xshift'] = np.zeros(len(df))
df['yshift'] = np.zeros(len(df))

elevations = list(set(df.el))
rotpposns = list(set(df.rotpposn))
print('Range of elevation:',np.sort(elevations))
print('Range of rotpposn:',np.sort(rotpposns),end='\n\n')

# running through all frames
print(f'Running through all {len(df)} frames.')
for i in df.index.values:
	if i%10 == 0: print(f'\nAt number {i} of {len(df)} frames...',end=' ')
	else: print(i,end=',')

	filename = home+date+'/'+df.loc[i,'file']
	#print(filename,end=', ')
	d1 = fits.getdata(filename)
	xshift,yshift = ir.cross_correlation_shifts(d0,d1) # returns xshift, yshift
	df.loc[i,'xshift'] = round(xshift,6) # enough precision
	df.loc[i,'yshift'] = round(yshift,6) # enough precision
	
print(end='\n\n')
print(df,end='\n\n')
print('Writing dataframe to new file.')

df.to_csv(f'../KVS-data/keck_FCS_{FCS_on_off}_{band}_measurements.dat',sep='\t',index=False)
# pet peeve of Taylor's is how pandas has 'delimiter' for pd.read_csv
# but requires 'sep' for df.to_csv...





