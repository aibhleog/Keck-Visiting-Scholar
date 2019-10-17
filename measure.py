'''
NOTE:   This script reads in data ran from a file that does not exist in this
            repository.  If you would like access to this file, please email
            the author and provide an explanation for why you would need it.

Code used to run the modules in this directory.  To do so, will read in the dataframe 
'keck_masks.dat' which holds the current MOSFIRE masks used to test this code.
'''

__author__ = 'Taylor Hutchison'
__email__ = 'aibhleog@tamu.edu'
__version__ = 'Oct2019'

from drift import *
from mask_drift import *
from seeing_map import *


# -- READING IN DATA -- #
df = pd.read_csv('KVS-data/keck_masks.dat',delimiter='|',
    converters={'star_slit': lambda x: x.split(','), 'star_cols': lambda x: x.split(',')})


#for indx in df.index.values: # running through all of it
for indx in [6]:   
    # -- Creating Drift() object -- #
    test = Drift()

    test.home = df.loc[indx,'path']
    test.date = df.loc[indx,'date']
    test.mask = df.loc[indx,'mask']
    test.dither = df.loc[indx,'dither']
    test.band = df.loc[indx,'band']

    test.row_start = int(df.loc[indx,'star_slit'][0])
    test.row_end = int(df.loc[indx,'star_slit'][1])
    test.col_start = int(df.loc[indx,'star_cols'][0])
    test.col_end = int(df.loc[indx,'star_cols'][1])
    
    # -- running seeing & drift maps -- #
    #frame,utc,seeing = get_seeing(drift_obj=test)
    #seeing_map(utc,seeing,drift_obj=test)#,savefig=True)
    #star_drift_map(*get_star_drift(drift_obj=test),drift_obj=test)#,savefig=True)
    
    ref = 'm181125_0215.fits'
    raw = 'm181125_0240.fits'
    
    
    print(test.cross_correlations(ref,ref))
    print(test.cross_correlations(ref,raw))