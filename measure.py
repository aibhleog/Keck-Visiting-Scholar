'''
NOTE:   This script reads in data ran from a file that does not exist in this
            repository.  If you would like access to this file, please email
            the author and provide an explanation for why you would need it.

Code used to run the modules in this directory.  To do so, will read in the dataframe 'keck_masks.dat' which holds the current MOSFIRE masks used to test this code.
'''

__author__ = 'Taylor Hutchison'
__email__ = 'aibhleog@tamu.edu'
__version__ = 'Sept2019'

import pandas as pd
from drift import *
from mask_drift import *
from seeing_map import *


# -- READING IN DATA -- #
df = pd.read_csv('plots-data/keck_masks.dat',delimiter='\s+',converters={'star_slit': lambda x: x.split(','),'star_cols': lambda x: x.split(',')})

# -- Creating Drift() object -- #
test = Drift()

test.date = df.loc[0,'date']
test.mask = df.loc[0,'mask']
test.dither = df.loc[0,'dither']
test.band = df.loc[0,'band']

test.row_start = df.loc[0,'star_slit']
test.row_end = 173
test.col_start = 810
test.col_end = 815

