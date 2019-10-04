'''
Code used to look at the current MOSFIRE FCS model. Model is described in "current_model.py" and by Nick Konidaris and Ryan Trainer (see "mosfire_fcs_model.pdf" in the MOSFIRE_information/ folder).
'''

__author__ = 'Taylor Hutchison'
__email__ = 'aibhleog@tamu.edu'
__version__ = 'Oct2019'

import matplotlib.animation as animation
from current_model import * # current model written up by Taylor Hutchison

def get_PA_Z(num):
    df = pd.read_csv('../KVS-data/keck_fcs_measurements.dat',delimiter='\s+')
    elevations = np.sort(list(set(df.el)))
    rotpposns = np.sort(list(set(df.rotpposn)))

    print('Range of elevation:',elevations)
    print('Range of rotpposn:',rotpposns,end='\n\n')

    Z = 90-np.linspace(elevations[0],elevations[-1],num)
    PA = np.linspace(rotpposns[0],rotpposns[-1],num)
    return PA,Z

def colors(num):
    '''
    Returns array of colors for a colormap.
    '''
    cmap = plt.get_cmap('viridis')
    return cmap(np.linspace(0,1.2,num+1))

def xyshift(num,savefig=True):
    plt.figure(figsize=(9,6))

    PA,Z = get_PA_Z(num)
    x0,y0 = flexure_comp(-90,45,'J') # reference frame

    for r in range(len(PA)):
        xshift,yshift = flexure_comp(np.radians(PA),np.radians(Z[r]),'J')
        plt.plot(x0-xshift,y0-yshift,color='k')

    #plt.colorbar()
    plt.xlabel('(x$_0 -$ x) [pixels]')
    plt.ylabel('(y$_0 -$ y) [pixels]')

    plt.tight_layout()
    if savefig == True: plt.savefig('model.png')
    plt.show()
    plt.close('all')

def yshift_rot(num,savefig=True):
    plt.figure(figsize=(9,6))

    PA,Z = get_PA_Z(num)
    cs = colors(num)
    x0,y0 = flexure_comp(-90,45,'J') # reference frame

    for r in range(len(PA)):
        xshift,yshift = flexure_comp(np.radians(PA),np.radians(Z[r]),'J')
        plt.scatter(PA,y0-yshift,edgecolor='k',s=60, color=cs[r])

    plt.xlabel('rotpposn [degrees]')
    plt.ylabel('(y$_0 -$ y) [pixels]')

    plt.tight_layout()
    if savefig == True: plt.savefig('model_yshift_rot.png')
    plt.show()
    plt.close('all')

def animate(num):
    '''
    This function animates the model given a range of PA and Zenith angle.

    INPUTS ----	PA:	position angle, aka rotpposn
                Z:  zenith angle, aka 90-elevation

    RETURNS --- animated plot walking through zenith angle.
    '''
    fig = plt.figure(figsize=(9,6))
    ax = plt.gca()
    ax = plt.axes(xlim=(-7,5),ylim=(-7,7))

    # initalizing plotting variables
    PA,Z = get_PA_Z(num)
    blank = np.zeros((2,len(PA)))

    line = plt.scatter(blank[0],blank[1],edgecolor='k',c=PA,cmap='viridis',s=120)
    tex = ax.text(0.97,0.91,'',ha='right',transform=ax.transAxes,fontsize=20)

    # plotting the outline of the entire model range
    for i in range(len(Z)):
        new_x, new_y = flexure_comp(np.radians(PA),np.radians(Z[i]),'J')
        plt.plot(new_x,new_y,color='k',zorder=0,lw=1)

    # colorbar legend
    ax.text(1.2,0.25,'rotpposn [degrees]',rotation=270,fontsize=18,transform=ax.transAxes)
    plt.colorbar()

    # need an initial setup function so the animation function can
    # anchor off of it -- this is essential!
    def init():
        global tex
        line.set_offsets(np.stack((blank[0],blank[1]),axis=1))
        tex.set_text('Zenith ang: 0$^o$')
        return line,tex,

    # the function that will actually be changing things in the animation
    def shift(e):
        new_x, new_y = flexure_comp(np.radians(PA),np.radians(Z[e]),'J')
        line.set_offsets(np.stack((new_x,new_y),axis=1))
        tex.set_text('Zenith ang: %.2f$^o$' %round(PA[e],2))
        return line,tex,

    # all the build up lead to this! Running the animation function...
    anim = animation.FuncAnimation(fig,shift,init_func=init,\
        frames=np.arange(len(Z)),interval=100,blit=True)

    ax.set_xlabel('(x$_0 -$ x) [pixels]')
    ax.set_ylabel('(y$_0 -$ y) [pixels]')

    plt.tight_layout()
    anim.save('shifts.gif', fps=5, writer='imagemagick',dpi=100) # this will take a while to make
    #plt.show() # doesn't work in Jupyter Lab
    plt.close('all')

    print('Figure saved.')


