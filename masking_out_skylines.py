'''
NOTE:   Currently still under construction!

This module will mask out skylines in raw MOSFIRE data, 
to be used in the mask_drift.py script.

EDIT: okay, so this kinda does that... in that it sigma clips
and ignores the lines by doing a running median.... so yeah.


NOTES:
OKay, so for now it does a decent job at showing the raw stellar 
spectra.  The colors of the lines are the airmass, the line types denote if the
seeing gets above 0.84" (where it becomes ls=":").

It's definitely affected by the seeing (as expected), but also lightly
affected by the airmass.  Need to think of how to properly account for this
so that we can really compare the flux changes to see if there's a drift.

'''

__author__ = 'Taylor Hutchison'
__email__ = 'aibhleog@tamu.edu'
__version__ = 'May2021'


from drift import *
from mask_drift import *
from seeing_map import *
import smoothing as sm


# from https://stackoverflow.com/questions/37671432/how-to-calculate-running-median-efficiently
from collections import deque
from bisect import insort, bisect_left
from itertools import islice
def running_median_insort(seq, window_size):
    """Contributed by Peter Otten"""
    seq = iter(seq)
    d = deque()
    s = []
    result = []
    for item in islice(seq, window_size):
        d.append(item)
        insort(s, item)
        result.append(s[len(d)//2])
    m = window_size // 2
    for item in seq:
        old = d.popleft()
        d.append(item)
        del s[bisect_left(s, old)]
        insort(s, item)
        result.append(s[m])
    return result



frame = 'm210423_0240.fits'

# -- READING IN DATA -- #
df = pd.read_csv('KVS-data/keck_masks.dat',delimiter='|',
    converters={'star_slit': lambda x: x.split(','), 'star_cols': lambda x: x.split(',')})
indx = len(df)-4



# -- Creating Drift() object -- #
test = Drift()

test.home = df.loc[indx,'path']
test.date = df.loc[indx,'date']
test.mask = df.loc[indx,'mask']
test.dither = df.loc[indx,'dither']
test.band = df.loc[indx,'band']

test.row_start = int(df.loc[indx,'star_slit'][0])
test.row_end = int(df.loc[indx,'star_slit'][1])
test.col_start = 0
test.col_end = 2048

# slicing out the star and masking out the skylines
spectrum = test.cut_out(frame)

profile = np.nansum(spectrum,axis=1)
loc = profile.tolist().index(max(profile))
spec = np.nansum(spectrum[loc-2:loc+3],axis=0)

notloc = loc+8
skylines = np.nansum(spectrum[notloc-2:notloc+3],axis=0)

plt.figure(figsize=(9,5))
#plt.imshow(spectrum,origin='lower')
#plt.plot(profile)
#plt.plot(spec)
#plt.plot(skylines)

diff = spec-skylines
plt.plot(diff)

# sigma clipping
med = sm.smooth(diff,181,window='flat')
mask = sigma_clip(diff-med,sigma=2)
diff[mask.mask] = med[mask.mask]
plt.plot(diff)

# running median
med = sm.smooth(diff,181,window='flat')
plt.plot(med)

total_flux = np.trapz(med)
# print(total_flux)


plt.tight_layout()
plt.savefig(f'plots-data/mosfire-{test.band}-skylines.pdf')
plt.close()




# running on a few frames
seeing = pd.read_csv(f'plots-data/seeing/seeing_map_{test.date}_{test.mask}.txt',sep='\t')
airmass = np.linspace(seeing.airmass.min(),seeing.airmass.max(), 15)
colors = plt.cm.RdBu(np.linspace(1,0, 15))
cindx = np.arange(len(colors))

plt.figure(figsize=(9,5))

for num in np.arange(220,274,5):
    frame = f'm210423_0{num}.fits'
    # slicing out the star and masking out the skylines
    spectrum = test.cut_out(frame)
    
    # getting airmass info from seeing df
    row = seeing.query(f'{num} == frame').copy()
    diff_airmass = abs(airmass-row.airmass.values[0])
    c = cindx[diff_airmass == min(diff_airmass)][0]
    
    profile = np.nansum(spectrum,axis=1)
    loc = profile.tolist().index(max(profile))
    spec = np.nansum(spectrum[loc-2:loc+3],axis=0)

    notloc = loc+8
    skylines = np.nansum(spectrum[notloc-2:notloc+3],axis=0)

    diff = spec-skylines

    # sigma clipping
    med = sm.smooth(diff,181,window='flat')
    mask = sigma_clip(diff-med,sigma=2)
    diff[mask.mask] = med[mask.mask]

    # running median
    med = sm.smooth(diff,181,window='flat')
    if row.seeing.values[0] > 0.84:
        plt.plot(med,color=colors[c],ls=':')
    else:
        plt.plot(med,color=colors[c])

    total_flux = np.trapz(med)
#     print(f'For m210423_0{num}.fits:',total_flux)
    print(f'airmass={round(row.airmass.values[0],2)}, seeing={round(row.seeing.values[0],2)}, \t{round(total_flux,2)}, \tand {c}')


plt.tight_layout()
plt.savefig(f'plots-data/mosfire-{test.band}-skylines.pdf')
plt.close()




















