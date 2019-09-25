'''
NOTE:   Currently still under construction!
        This script reads in data ran from a script that does not exist in this
            repository.  If you would like access to this script, please email
            the author and provide an explanation for why you would need it.

This script is used to look at how the shifts work. From the source code:
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
df = pd.read_csv(home+date+'/fcs_info.dat',delimiter='\s+')

# adding columns for xshift and yshift
df['xshift'] = np.zeros(len(df))
df['yshift'] = np.zeros(len(df))

print('Starting the cross_correlation_shifts() function.')
elevations = list(set(df.el))
# running through set of elevation
for j in range(len(elevations)):
	print(f'Starting on elevation {elevations[j]}...')	
	el_df = df.query(f'el == {elevations[j]}').copy() # important to .copy()
	indx = el_df.index.values
	
	d0 = fits.getdata(home+date+'/'+el_df.loc[indx[0],'file']) # first frame
	# now running through the rows with this elevation
	for i in np.arange(1,len(el_df)): # skiping the first frame
		d1 = fits.getdata(home+date+'/'+el_df.loc[indx[i],'file'])
		xshift,yshift = ir.cross_correlation_shifts(d0,d1) # returns xshift, yshift
		df.loc[indx[i],'xshift'] = xshift
		df.loc[indx[i],'yshift'] = yshift
		if i == len(el_df)-1: 
			print(f'Finished with elevation {elevations[j]}, moving on...',end='\n\n')
	
print(df,end='\n\n')
print('Writing dataframe to new file.')

df.to_csv('../KVS-data/keck_fcs_measurements.dat',sep='\t',index=False)
# pet peeve of Taylor's is how pandas has 'delimiter' for pd.read_csv
# but requires 'sep' for df.to_csv...






