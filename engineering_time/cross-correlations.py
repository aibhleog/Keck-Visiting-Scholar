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

Reference frame: el=45, rotpposn=-90 (chosen because oreintation for flats)
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

parser.add_argument('-p','--path',help='Path to files.',required=True)
parser.add_argument('-d','--date',help='Date files were taken.',required=True)
args = parser.parse_args()


# reading in data
print('Reading in data.',end='\n\n')
home = args.path
date = args.date
files = np.loadtxt(home+date+'/files.list',dtype='str')
org_df = pd.read_csv(home+date+'/fcs_info.dat',delimiter='\s+')

# -- clipping out bad target2 values -- #
t2 = org_df.mode().loc[0,'target2'] # mode value for this keyword
df = org_df.query(f'{t2-t2*0.2} > target2 > {t2+t2*0.2}').copy()
df.reset_index(inplace=True)

# -- reference frame -- #
ref_df = df.query('el == 45 and rotpposn == -90').copy()
ref_df.reset_index(inplace=True) # making ref_df because there can be > 1 match
reference = ref_df.loc[0,'file']
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
for i in np.arange(len(df)):
	if i%10 == 0: print(f'At number {i} of {len(df)} frames...')
	d1 = fits.getdata(home+date+'/'+df.loc[i,'file'])
	xshift,yshift = ir.cross_correlation_shifts(d0,d1) # returns xshift, yshift
	df.loc[i,'xshift'] = round(xshift,6) # enough precision
	df.loc[i,'yshift'] = round(yshift,6) # enough precision
	
print(df,end='\n\n')
print('Writing dataframe to new file.')

df.to_csv('../KVS-data/keck_fcs_measurements.dat',sep='\t',index=False)
# pet peeve of Taylor's is how pandas has 'delimiter' for pd.read_csv
# but requires 'sep' for df.to_csv...






