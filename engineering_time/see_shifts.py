'''
NOTE:   Currently still under construction!
        This script reads in data ran from the cross-correlations script in this
            repository.  If you would like access to this data, please email
            the author and provide an explanation for why you would need it.

'''

__author__ = 'Taylor Hutchison'
__email__ = 'aibhleog@tamu.edu'
__version__ = 'Sept2019'

from visualize import *

# reading in the data
df = pd.read_csv('../KVS-data/keck_fcs_measurements.dat',delimiter='\s+')
elevations = list(set(df.el))
rotpposns = list(set(df.rotpposn))
print('Range of elevation:',np.sort(elevations))
print('Range of rotpposn:',np.sort(rotpposns),end='\n\n')

# looking at x and y shifts with coloring based upon rotpposn
xyshift(df)

xshift_rot(df)

yshift_rot(df)

xshift_el(df)

yshift_el(df)








