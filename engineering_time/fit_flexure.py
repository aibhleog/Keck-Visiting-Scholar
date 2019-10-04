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
df = pd.read_csv('../KVS-data/keck_fcs_measurements.dat',delimiter='\s+')
elevations = np.sort(list(set(df.el)))
rotpposns = np.sort(list(set(df.rotpposn)))
print('Range of elevation:',elevations)
print('Range of rotpposn:',rotpposns,end='\n\n')


# visualize the data
plt.figure(figsize=(9,6))
gs = gd.GridSpec(2,1,height_ratios=[3,1])

ax = plt.subplot(gs[0])
ax.scatter(df.rotpposn,df.yshift,c=df.el,cmap='viridis',s=60,edgecolor='k',zorder=5)
ax.set_xticks(rotpposns)

x = np.linspace(rotpposns[0],rotpposns[-1],200)
def fit(rot,el,A,B,C):
	shift = np.pi/0.53
	return np.sin(rot/A+shift)*np.power(el,B)+C*el

# ---------------------------------------- #
# -- color scheme and kwargs for legend -- #
cmap = plt.get_cmap('viridis')
colors = cmap(np.linspace(0,1.2,len(elevations)+1))
ty,tys,tx,txs = 0.28,0.105,0.2,0.05
# ---------------------------------------- #

# making dataframe to log fits
ones = np.ones(len(elevations))
fits = pd.DataFrame({'el':elevations,'A':ones,'B':ones,'C':ones})
for e in range(len(elevations)):	
	el = elevations[e] # sorting by elevation
	p0 = [el,55.5,0.54,0.6] # initial guess used in curve_fit
	yvals = df.query(f'el == {el}').yshift
	rots = df.query(f'el == {el}').rotpposn
	popt,pcov = curve_fit(fit,rots,yvals,p0=p0, 	# fit; using bounds to make sure 
		bounds=((el-el*0.01,55,-np.inf,-np.inf), 	# el doesn't shift, also working to find
				(el+el*0.01,56,np.inf,np.inf)))		# constant coefficients
	ax.plot(x,fit(x,*popt),color=colors[e])
	ax.plot()
    
	# adding legend for colors
	'''kwargs = {'color':colors[e],'transform':ax.transAxes,'fontsize':15}
	if e < 3: txt = ax.text(tx,ty-tys*e,el,**kwargs)
	elif e < 6: txt = ax.text(tx+txs,ty-tys*(e-3),el,**kwargs)
	elif e < 9: txt = ax.text(tx+txs*2,ty-tys*(e-6),el,**kwargs)
	elif e < 11: txt = ax.text(tx+txs*3,ty-tys*(e-9),el,**kwargs)	
	else: txt = ax.text(tx+txs*4,ty-tys*(e-11),el,**kwargs)
	txt.set_path_effects([PathEffects.withStroke(linewidth=1.2, foreground='k')])'''

	# adding fits to dataframe
	fits.loc[e,'A'] = popt[1]
	fits.loc[e,'B'] = popt[2]
	fits.loc[e,'C'] = popt[3]

# labels
txt = ax.text(tx-0.015	,ty+0.1,'elevation [degrees]',color='k',transform=ax.transAxes,fontsize=15)
txt.set_path_effects([PathEffects.withStroke(linewidth=0.6, foreground='k')])
ax.set_title('Reference frame: EL=45$^\mathrm{o}$ ROTPPOSN=-90$^\mathrm{o}	$')
ax.set_ylabel('(y$_0 -$ y) [pixels]')
ax.set_xticklabels([])

# residual subplot
ax = plt.subplot(gs[1])
for e in range(len(elevations)):
	yvals = df.query(f'el == {el}').yshift
	rots = df.query(f'el == {el}').rotpposn
	coeffs = [fits.loc[e,j] for j in ['A','B','C']]
	
	line_fit = fit(rots,elevations[e],*coeffs)
	ax.scatter(rots,line_fit-yvals,color=colors[e],s=60,edgecolor='k')
ax.axhline(0,ls=':',color='k',zorder=0)

# labels
ax.set_ylabel('res')
ax.set_xlabel('rotpposn [degrees]')
ax.set_xticks(rotpposns)

plt.tight_layout()
plt.savefig('yshift_rot.png')
plt.show()
plt.close('all')






