'''
NOTE:   Currently still under construction!
        This script reads in data ran from the cross-correlations script in this
            repository.  If you would like access to this data, please email
            the author and provide an explanation for why you would need it.
'''

__author__ = 'Taylor Hutchison'
__email__ = 'aibhleog@tamu.edu'
__version__ = 'Sept2019'

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gd

# reading in the data
org_df = pd.read_csv('../KVS-data/keck_fcs_measurements.dat',delimiter='\s+')

# -- clipping out bad target2 values -- #
t2 = org_df.mode().loc[0,'target2'] # mode value for this keyword
#df = org_df.query(f'{t2-t2*0.2} > target2 > {t2+t2*0.2}').copy()
#df.reset_index(inplace=True)
df = org_df.copy()

# visualize the data
plt.figure(figsize=(9,6))
elevations = list(set(df.el))
rotpposn = np.sort(list(set(df.rotpposn)))

# running through set of elevation
for j in range(len(elevations)):
	el_df = df.query(f'el == {elevations[j]}').copy() # important to .copy()
	plt.scatter(el_df.xshift,el_df.yshift,c=el_df.rotpposn,cmap='viridis',edgecolor='k',zorder=5)
	plt.plot(el_df.xshift,el_df.yshift,color='gray',zorder=0)
	
cbar = plt.colorbar()
cbar.set_ticks(rotpposn)
plt.text(1.21,0.4,'rotpposn',rotation=270,transform=plt.gca().transAxes,fontsize=16)

plt.xlabel('(x$_0 -$ x)$_{elevation}$ [pixels]')
plt.ylabel('(y$_0 -$ y)$_{elevation}$ [pixels]')

plt.tight_layout()
plt.savefig('test.png')
plt.close('all')


# NOW IN 3D
# visualize the data
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import
fig = plt.figure(figsize=(9,6))
ax = fig.add_subplot(111, projection='3d')

elevations = list(set(df.el))
rotpposn = np.sort(list(set(df.rotpposn)))

cmap = plt.get_cmap('RdBu')
colors = cmap(np.linspace(0,1,len(elevations)+1))

# running through set of elevation
for j in range(len(elevations)):
	el_df = df.query(f'el == {elevations[j]}').copy() # important to .copy()
	ax.scatter(el_df.xshift,el_df.yshift,el_df.rotpposn,edgecolor='k',
		alpha=1.,color=colors[j],s=100,zorder=5)

ax.azim = 200
ax.elev = 35
	
ax.set_xlabel('(x$_0 -$ x)$_{elevation}$ [pixels]',labelpad=15)
ax.set_ylabel('(y$_0 -$ y)$_{elevation}$ [pixels]',labelpad=15)
ax.set_zlabel('rotpposn [degrees]',labelpad=15)
ax.set_zticklabels(rotpposn)

plt.tight_layout()
plt.savefig('test3d.png')
plt.close('all')








