'''
NOTE:   This script reads in data ran from a file that does not exist in this
            repository.  If you would like access to this file, please email
            the author and provide an explanation for why you would need it.

Code used to run the modules in this directory.  To do so, will read in the dataframe 
'keck_masks.dat' which holds the current MOSFIRE masks used to test this code.
'''

__author__ = 'Taylor Hutchison'
__email__ = 'aibhleog@tamu.edu'
__version__ = 'Feb2020'

from drift import *
from mask_drift import *
from seeing_map import *


# -- READING IN DATA -- #
df = pd.read_csv('KVS-data/keck_masks.dat',delimiter='|',
    converters={'star_slit': lambda x: x.split(','), 'star_cols': lambda x: x.split(',')})


#for indx in df.index.values: # running through all of it
for indx in [len(df)-1]:   
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

    print('Date:', test.date, 'Mask:', test.mask)

    # -- looking at profiles -- #
    #nod_A, nod_B = test.split_dither()
    #test.show_me_all_profiles(nod_A)
    #test.show_me_all_profiles(nod_B)	

    # -- running seeing & drift maps -- #
    frame,utc,seeing,airmass = get_seeing(drift_obj=test)
    seeing_map(utc,seeing,airmass,drift_obj=test,savefig=True,see=False)
    print(seeing)
    #drift_map(*get_star_drift(drift_obj=test),drift_obj=test,savefig=False,see=False)

#     info_A, info_B = get_slit_drift(drift_obj=test)
#     frames,shifts = [info_A[0],info_B[0]],[info_A[1],info_B[1]]
    #drift_map(frames,[shifts[0][1],shifts[1][1]],drift_obj=test,star=False,savefig=True) # marks for slit

    # saving values to files
    # (using pandas because my brain works that way)
    # ----------------------------------------------
    # seeing map (with airmass)
    '''time_only = [[i.strftime('%H:%M:%S.%f') for i in utc[0]],
                 [i.strftime('%H:%M:%S.%f') for i in utc[1]]]

    nod = np.chararray((len(frame[0])))
    nodA, nodB = nod.copy(), nod.copy()
    nodA[:] = 'A'; nodB[:] = 'B'
    
    dsA = pd.DataFrame({'frame':frame[0], 'utc':time_only[0], 
                        'seeing':seeing[0], 'airmass':airmass[0], 'nod':nodA})
    dsB = pd.DataFrame({'frame':frame[1], 'utc':time_only[1], 
                        'seeing':seeing[1], 'airmass':airmass[1], 'nod':nodB})
    
    ds = pd.concat([dsA,dsB])
    ds.sort_values(by=['frame'],inplace=True)
    ds.reset_index(inplace=True,drop=True)
    '''
    #ds.to_csv(f'plots-data/seeing/seeing_map_{test.date}_{test.mask}.txt',
    #              sep='\t',index=False)
