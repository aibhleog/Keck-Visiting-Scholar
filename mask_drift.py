import pandas as pd
from drift import *

df = pd.read_csv('/home/aibhleog/Desktop/observing/drift/Keck-Visiting-Scholar/'
                 'plots-data/keck_masks.dat',delimiter='\s+')

# TESTING ON 2018DEC12 DATA for COSMOS
test = Drift()

test.date = '2018nov25'
test.mask = 'UDS_2018B_J'
test.dither = 1.5
test.band = 'J'

test.row_start = 92
test.row_end = 173
test.col_start = 810
test.col_end = 815


# -- getting list of files for both dithers
home = '/home/aibhleog/Desktop/observing/'
#home = '/run/media/aibhleog/eve_lily/observing-keck2018/'
all_frames = test.mask_frames(home=home)
nod_A, nod_B = test.split_dither(all_frames,home=home)


# ------------- measuring the fits ------------- #
# ---------------------------------------------- #
mean, A, sig, num = test.fit_all(nod_A,home=home)   
df_A = pd.DataFrame({'frame':num,'cen':mean,'A':A,'sig':sig})

mean, A, sig, num = test.fit_all(nod_B,home=home)   
df_B = pd.DataFrame({'frame':num,'cen':mean,'A':A,'sig':sig})
# ---------------------------------------------- #

df_A['offset'] = (df_A.loc[0,'cen']-df_A.cen.values) * 0.18 # "/pixel
df_B['offset'] = (df_B.loc[0,'cen']-df_B.cen.values) * 0.18 # "/pixel
df_A['seeing'] = df_A.sig.values * 2.35 * 0.18 # "/pixel
df_B['seeing'] = df_B.sig.values * 2.35 * 0.18 # "/pixel


# LOOKING AT THE DATA

# -- OFFSET AS FUNCTION OF TIME (i.e., FRAME) -- #
# ---------------------------------------------- #
plt.figure(figsize=(9,6))
plt.scatter(df_A.frame,df_A.offset,edgecolor='k',s=60,label='Nod A')
plt.scatter(df_B.frame,df_B.offset,edgecolor='k',marker='^',s=60,label='Nod B')

plt.text(0.975,0.05,'Mask: %s'%(test.mask),ha='right',\
         transform=plt.gca().transAxes,fontsize=15)
plt.text(0.975,0.1,'Date: %s'%(test.date),ha='right',\
         transform=plt.gca().transAxes,fontsize=16)

plt.legend(loc=2)
plt.xlabel('frame number')
plt.ylabel('$y_0 - y$ ["]')
plt.ylim(-0.2,0.4)

plt.tight_layout()
plt.show()
plt.close()
# ============================================== #


# -- SEEING MAP AS FUNCTION OF TIME (i.e., FRAME) -- #
# -------------------------------------------------- #
plt.figure(figsize=(9,6))
plt.scatter(df_A.frame,df_A.seeing,edgecolor='k',s=60,label='Nod A')
plt.scatter(df_B.frame,df_B.seeing,edgecolor='k',marker='^',s=60,label='Nod B')

plt.text(0.975,0.92,'Mask: %s'%(test.mask),ha='right',\
         transform=plt.gca().transAxes,fontsize=15)
plt.text(0.975,0.88,'Date: %s'%(test.date),ha='right',\
         transform=plt.gca().transAxes,fontsize=16)

plt.legend(loc=2)
plt.xlabel('frame number')
plt.ylabel('seeing ["]')
plt.ylim(0.4,1.6)

plt.tight_layout()
plt.show()
plt.close()
# ================================================== #

test.show_me_all_profiles(np.concatenate((nod_A,nod_B)),home=home)