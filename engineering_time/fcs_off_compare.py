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
band = 'H'  # J or H
df = pd.read_csv(f'../KVS-data/individual_FCS_datasets/keck_FCS_Off_{band}_measurements.dat',\
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
plt.figure(figsize=(9,6))
gs = gd.GridSpec(2,1,height_ratios=[3,1])

ax = plt.subplot(gs[0]) # main plot
ax2 = plt.subplot(gs[1]) # residual subplot

for e in range(len(elevations)):
    el = elevations[e] # sorting by elevation

    subdf = df.query('el == %s'%el).copy()
    ax.scatter(subdf.rotpposn,subdf.yshift,color=colors[e],s=60,edgecolor='k',zorder=5,\
              label='El: %s'%el)
    ax.set_xticks(rotpposns)

    # plotting current model
    x0,y0 = flexure_comp(-90,45,band) # reference frame
    yvals = subdf.yshift
    rots = subdf.rotpposn

    # adding current model
    if band == 'H': phase_coeff = -1/4
    elif band == 'J': phase_coeff = 2/3
    phase_shift = phase_coeff*np.pi
        
    xshift,yshift = flexure_comp(np.radians(rots)+phase_shift,np.radians(90-el),band) # 90-el because zenith
    ax.text(0.025,0.11,f'Added phase shift of {round(phase_coeff,2)}$\pi$',transform=ax.transAxes,fontsize=13)
    
    if band == 'H': manual_y0 = -4
    elif band == 'J': manual_y0 = -3.5
    
    mod_yvals = manual_y0-yshift # have to manually shift for now
    ax.text(0.025,0.05,f'Manually shifted yvalues: y_new = {manual_y0}-y',transform=ax.transAxes,fontsize=13)
    
    ax.plot(rots,mod_yvals,zorder=0,lw=1,color=colors[e])
    
    # residual subplot
    ax2.scatter(rots,yvals-mod_yvals,color=colors[e],s=60,edgecolor='k')
    ax2.axhline(0,ls=':',color='k',zorder=0)
    
txt = ax.text(0.028,0.9,band,fontsize=18,transform=ax.transAxes,color='C0')
txt.set_path_effects([PathEffects.withStroke(linewidth=1.5, foreground='k')])

# labels
ax.set_title('Reference frame: EL=45$^\mathrm{o}$ ROTPPOSN=-90$^\mathrm{o}$ $-$ model manually shifted',fontsize=14)
ax.set_ylabel('(y$_0 -$ y) [pixels]')
ax.set_xticklabels([])
#ax.set_ylim(-8.6,2.2)
ax.legend(loc=3,bbox_to_anchor=(1,0),fontsize=12)

# labels
ax2.set_ylabel('res')
ax2.set_xlabel('rotpposn [degrees]')
ax2.set_xticks(rotpposns)

plt.tight_layout()
#plt.savefig('../plots-data/data_FCS/eng_EL%s.pdf'%el)
#plt.savefig(f'../plots-data/data_FCS/model_fit_to_data-{band}.pdf')
plt.show()
plt.close('all')






