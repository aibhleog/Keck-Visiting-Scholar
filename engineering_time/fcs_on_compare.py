'''
Code used to fix the internal flexure in one reference frame. We plan to compare to the actual FCS model to see the differences.
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
from current_model import * # current model written up by Taylor

# reading in the data
band = 'J'  # J or H
df = pd.read_csv(f'../KVS-data/individual_FCS_datasets/keck_FCS_On_{band}_measurements.dat',\
                 delimiter='\t')
elevations = np.sort(list(set(df.el)))
rotpposns = np.sort(list(set(df.rotpposn)))
#elevations = elevations[5:]
print('Range of elevation:',elevations)
print('Range of rotpposn:',rotpposns,end='\n\n')

# -- color scheme and kwargs for legend -- #
cmap = plt.get_cmap('viridis')
colors = cmap(np.linspace(0,1.2,len(elevations)+1))
# ---------------------------------------- #


# visualize the data
plt.figure(figsize=(9,5))
gs = gd.GridSpec(2,1,height_ratios=[2,1])

ax = plt.subplot(gs[0]) # main plot
ax2 = plt.subplot(gs[1]) # subplot to show El=15

for e in range(len(elevations)):
    el = elevations[e] # sorting by elevation

    subdf = df.query('el == %s'%el).copy()
    if el > 30:
        ax.scatter(subdf.rotpposn,subdf.yshift,color=colors[e],s=60,edgecolor='k',zorder=5,\
                  label='El: %s'%el)
    else:
        ax2.scatter(subdf.rotpposn,subdf.yshift,color=colors[e],s=60,edgecolor='k',zorder=5,\
                  label='El: %s'%el)

ax.axhline(0,ls=':',color='k')
txt = ax.text(0.028,0.08,band,fontsize=18,transform=ax.transAxes,color='C0')
txt.set_path_effects([PathEffects.withStroke(linewidth=1.5, foreground='k')])
    
# labels
ax.set_title('FCS is on; Reference frame: EL=45$^\mathrm{o}$ ROTPPOSN=-90$^\mathrm{o}$',fontsize=14)
ax.set_ylabel('(y$_0 -$ y) [pixels]')
ax.set_xticklabels([])
ax.set_xticks(rotpposns)
ax.legend(loc=3,bbox_to_anchor=(1,0),fontsize=12)

# labels
#ax2.set_ylabel('res')
ax2.set_xlabel('rotpposn [degrees]')
ax2.set_xticks(rotpposns)
ax2.legend(loc=3,bbox_to_anchor=(1,0),fontsize=12)

plt.tight_layout()
#plt.savefig(f'../plots-data/data_FCS/correlations_FCS_On-{band}.pdf')
plt.show()
plt.close('all')






