import numpy as np
from iexplot.pynData import *
#==============================================================================
# Utils for cropping, rotating and symmetrization
#==============================================================================
def val_to_idx(x, val):
    '''
    Internal methods for converting values to indices
    
    x:              1D array, monotonic
    val:            A value
    '''
    idx = np.nanargmin((x-val)**2)
    
    return idx


def lim_to_bounds(x, ROI):
    '''
    Internal methods for converting values to indices
    
    x:              1D array, monotonic
    ROI:            A list in the format [xmin, xmax]
    '''
    idx0 = np.nanargmin((x-ROI[0])**2)
    idx1 = np.nanargmin((x-ROI[1])**2)
    idmin = np.min([idx0, idx1])
    if idmin<0:
        idmin = 0
    idmax = np.max([idx0, idx1])
    if idmax>len(x)-1:
        idmax = len(x)-1
    
    return idmin, idmax


def crop(d, ax, ROI):
    '''
    Cropping data along a given axis.
    Perform the operation one axis at a time if cropping along multiple dim
    is needed
    
    Input:
    d:              nData instance to be cropped
    ax:             Use 'x', 'y' or 'z'
    ROI:            A list in the format of [axMin, axMax]
    
    Returns:
    d_c:            Cropped nData instance
    '''
    idmin, idmax = lim_to_bounds(d.scale[ax], ROI)
    dim = len(d.data.shape)
    if dim==1:
        if ax=='x':
            d_c = nData(d.data[idmin:idmax])
    elif dim==2:
        if ax=='y':
            d_c = nData(d.data[idmin:idmax])
        elif ax=='x':
            d_c = nData(d.data[:, idmin:idmax])
    elif dim==3:
        if ax=='z':
            d_c = nData(d.data[idmin:idmax])
        elif ax=='y':
            d_c = nData(d.data[:, idmin:idmax])
        elif ax=='x':
            d_c = nData(d.data[:, :, idmin:idmax])
    else:
        print('Warning: cropping a non-existent dim.')
    
    for key in d.unit.keys():
        if key==ax:
            d_c.updateAx(key, d.scale[key][idmin:idmax], d.unit[key])
        else:
            d_c.updateAx(key, d.scale[key], d.unit[key])

    return d_c


def rotatePlot2D(d, CCWdeg, center, plotRot=False):
    '''
    Rotate CCW relative to a point in the 2D plane. Use negative value for CW rotation
    We only provide the rotated axes, while the data is not rotated
    
    Inputs:
    CCWdeg:         In degrees and has to be in [-90 deg, 90 deg]
    xyCenter:       The center of rotation
    plotRot:        Optional. Whether or not to compare the 'before' and 'after'
    
    The coordinate transformation for the unit vectors:
                            |cos(deg)   -sin(deg)|
    (e_x' e_y') = (e_x e_y) |                    |
                            |sin(deg)    cos(deg)|
    And for the coordinates:
    
    |x'|   |cos(deg)   -sin(deg)| |x|
    |  | = |                    | | |
    |y'|   |sin(deg)    cos(deg)| |y|
    '''
    # ndimage.rotate(img2D, deg_in_pix) will not work. 
    # The shape of the rotated 2D img and the rotated scales
    # cannot be determined easily
    img = d.data
    xScale = d.scale['x']
    yScale = d.scale['y']
    
    xCenter = center[0]
    yCenter = center[1]

    # If we only want to plot a figure rotated, we then just need rotxx, rotyy
    xx, yy = np.meshgrid(xScale, yScale)
    rotxx = np.cos(CCWdeg*np.pi/180)*(xx-xCenter)-np.sin(CCWdeg*np.pi/180)*(yy-yCenter)+xCenter
    rotyy = np.sin(CCWdeg*np.pi/180)*(xx-xCenter)+np.cos(CCWdeg*np.pi/180)*(yy-yCenter)+yCenter
    
    if plotRot:
        fig, ax = plt.subplots(1,2)
        ax[0].pcolormesh(xx, yy, img)
        ax[0].set_aspect(1)
        ax[0].set_title('Before')

        ax[1].pcolormesh(rotxx, rotyy, img)
        ax[1].set_aspect(1)
        ax[1].set_title('After')
        
        fig.suptitle('CCW rotation {} deg'.format(CCWdeg))
        fig.tight_layout()
    
    return rotxx, rotyy


def _rotate2D(img, xScale, yScale, CCWdeg, center, newhscale=[], newvscale=[], plotRot=False):
    '''
    Internal methods
    
    Rotate CCW relative to a point in the 2D plane. Use negative value for CW rotation
    
    The coordinate transformation for the unit vectors:
                            |cos(deg)   -sin(deg)|
    (e_x' e_y') = (e_x e_y) |                    |
                            |sin(deg)    cos(deg)|
    And for the coordinates:
    
    |x'|   |cos(deg)   -sin(deg)| |x|
    |  | = |                    | | |
    |y'|   |sin(deg)    cos(deg)| |y|
    
    With a simple for loop, 3D rotation could be performed.
    
    Inputs:
    CCWdeg:         In degrees and has to be in [-90 deg, 90 deg]
    center:         The center of rotation. A list.
    newhscale:      Optional. Default is []. For a customized new horizontal scale
                    for output. The format is [vmin, vmax, num]
    plotRot:        Optional. Whether or not to compare the 'before' and 'after'
    '''
    # ndimage.rotate(img2D, deg_in_pix) will not work. 
    # The shape of the rotated 2D img and the rotated scales
    # cannot be determined easily
    
    xCenter = center[0]
    yCenter = center[1]

    # If we only want to plot a figure rotated, we then just need rotxx, rotyy
    xx, yy = np.meshgrid(xScale, yScale)
    rotxx = np.cos(CCWdeg*np.pi/180)*(xx-xCenter)-np.sin(CCWdeg*np.pi/180)*(yy-yCenter)+xCenter
    rotyy = np.sin(CCWdeg*np.pi/180)*(xx-xCenter)+np.cos(CCWdeg*np.pi/180)*(yy-yCenter)+yCenter

    # As the rotxx, rotyy are not linear grids, we need to flatten them into (x,y) pairs

    points = np.vstack((rotxx.flatten(), rotyy.flatten())).transpose()
    values = img.flatten()

    # Setting up the new grid
    rotXmin = rotxx.min()
    rotXmax = rotxx.max()
    rotYmin = rotyy.min()
    rotYmax = rotyy.max()
    numX = int(np.abs((rotXmax-rotXmin)/(xScale[1]-xScale[0]))+1)
    numY = int(np.abs((rotYmax-rotYmin)/(yScale[1]-yScale[0]))+1)
    newX = np.linspace(rotXmin, rotXmax, num=numX)
    newY = np.linspace(rotYmin, rotYmax, num=numY)

    if not newhscale==[]:
        newX = np.linspace(newhscale[0], newhscale[1], num=newhscale[2])

    if not newvscale==[]:
        newY = np.linspace(newvscale[0], newvscale[1], num=newvscale[2])
    
    newXX, newYY = np.meshgrid(newX, newY)

    # Interpolate
    newImg = interpolate.griddata(points, values, (newXX, newYY), method='cubic')
    
    if plotRot:
        fig, ax = plt.subplots(1,3)
        ax[0].pcolormesh(xx, yy, img)
        ax[0].set_aspect(1)
        ax[0].set_title('Before')

        ax[1].pcolormesh(rotxx, rotyy, img)
        ax[1].set_aspect(1)
        ax[1].set_title('After')

        ax[2].pcolormesh(newXX, newYY, newImg)
        ax[2].set_aspect(1)
        ax[2].set_title('Interped')

        fig.suptitle('CCW rotation {} deg'.format(CCWdeg))
        fig.tight_layout()
    
    return newImg, newX, newY


def rotate2D(d, CCWdeg, center, newhscale=[], newvscale=[], plotRot=False):
    '''
    Rotate CCW relative to a point in the 2D plane.
    
    Inputs:
    CCWdeg:         In degrees and has to be in [-90 deg, 90 deg]
                    Use negative value for CW rotation.
    center:         The center of rotation. A list.
    newhscale:      Optional. Default is []. For a customized new horizontal scale
                    for output. The format is [vmin, vmax, num]
    plotRot:        Optional. Whether or not to compare the 'before' and 'after'
    '''
    img = d.data
    xScale = d.scale['x']
    yScale = d.scale['y']
    
    newImg, newX, newY = _rotate2D(img, xScale, yScale, CCWdeg, center, newhscale=newhscale, newvscale=newvscale, plotRot=plotRot)
    
    d_rot = nData(newImg)
    d_rot.updateAx('x', newX, d.unit['x'])
    d_rot.updateAx('y', newY, d.unit['y'])
    
    return d_rot

def rotate3D(d, ax, CCWdeg, center, newhscale=[], newvscale=[], plotRot=False):
    '''
    Rotate CCW relative to a point in the 2D plane for a 3D stack.
    Note we have to rotate along x, y or z axis.
    
    Inputs:
    d:              nData instance
    ax:             Use 'x', 'y' or 'z'
    CCWdeg:         In degrees and has to be in [-90 deg, 90 deg].
                    Use negative value for CW rotation
    center:         The center of rotation. A list.
    newhscale:      Optional. Default is []. For a customized new horizontal scale
                    for output. The format is [vmin, vmax, num]
    plotRot:        Optional. Whether or not to compare the 'before' and 'after'
                    Only the first image 
    '''
    if ax=='z':
        newImg, newX, newY = _rotate2D(d.data[0], d.scale['x'], d.scale['y'], CCWdeg, center, 
                                       newhscale=newhscale, newvscale=newvscale, plotRot=plotRot)
        newStk = np.zeros((d.data.shape[0], newImg.shape[0], newImg.shape[1]))
        newStk[0] = newImg
        
        for i in range(1, d.data.shape[0]):
            # Pass on the scales to be consistent
            newImg, _, _ = _rotate2D(d.data[i], d.scale['x'], d.scale['y'], CCWdeg, center, 
                                     newhscale=[newX[0], newX[-1], len(newX)], 
                                     newvscale=[newY[0], newY[-1], len(newY)], plotRot=False)
            newStk[i] = newImg
            
        d_rot = nData(newStk)
        d_rot.updateAx('x', newX, d.unit['x'])
        d_rot.updateAx('y', newY, d.unit['y'])
        d_rot.updateAx('z', d.scale['z'], d.unit['z'])
    elif ax=='y':
        newImg, newX, newY = _rotate2D(d.data[:,0,:], d.scale['x'], d.scale['z'], CCWdeg, center, 
                                       newhscale=newhscale, newvscale=newvscale, plotRot=plotRot)
        newStk = np.zeros((newImg.shape[0], d.data.shape[1], newImg.shape[1]))
        newStk[:,0,:] = newImg
        
        for i in range(1, d.data.shape[1]):
            # Pass on the scales to be consistent
            newImg, _, _ = _rotate2D(d.data[:,i,:], d.scale['x'], d.scale['z'], CCWdeg, center, 
                                     newhscale=[newX[0], newX[-1], len(newX)], 
                                     newvscale=[newY[0], newY[-1], len(newY)], plotRot=False)
            newStk[:,i,:] = newImg
            
        d_rot = nData(newStk)
        d_rot.updateAx('x', newX, d.unit['x'])
        d_rot.updateAx('y', d.scale['y'], d.unit['y'])
        d_rot.updateAx('z', newY, d.unit['z'])
    elif ax=='x':
        newImg, newX, newY = _rotate2D(d.data[:,:,0], d.scale['y'], d.scale['z'], CCWdeg, center, 
                                       newhscale=newhscale, newvscale=newvscale, plotRot=plotRot)
        newStk = np.zeros((newImg.shape[0], newImg.shape[1], d.data.shape[2]))
        newStk[:,:,0] = newImg
        
        for i in range(1, d.data.shape[2]):
            # Pass on the scales to be consistent
            newImg, _, _ = _rotate2D(d.data[:,:,i], d.scale['y'], d.scale['z'], CCWdeg, center, 
                                     newhscale=[newX[0], newX[-1], len(newX)], 
                                     newvscale=[newY[0], newY[-1], len(newY)], plotRot=False)
            newStk[:,:,i] = newImg
            
        d_rot = nData(newStk)
        d_rot.updateAx('x', d.scale['x'], d.unit['x'])
        d_rot.updateAx('y', newX, d.unit['y'])
        d_rot.updateAx('z', newY, d.unit['z'])
    
    return d_rot


def sym2D(d, nfold, center, newhscale, newvscale, plotSym=False):
    '''
    Symmetrizing in 2D. 
    
    Inputs:
    nfold:          A integer - 4 for 4-fold, 6 for 6-fold.
                    nfold=2 means inversion not mirroring.
    center:         The center of rotation. A list.
    newhscale:      A customized new horizontal scale for output.
                    The format is [vmin, vmax, num].
                    Unlike rotate2D, this is a mandatory input.
    plotRot:        Optional. Whether or not to compare the 'before' and 'after'
    '''
    img = d.data
    xScale = d.scale['x']
    yScale = d.scale['y']
    
    if type(nfold)==int and nfold>1:
        newImg, newX, newY = _rotate2D(img, xScale, yScale, 0., center, newhscale=newhscale, newvscale=newvscale, plotRot=False)
        symImg = newImg

        for i in range(1, nfold):
            newImg, _, _ = _rotate2D(img, xScale, yScale, 360./nfold*i, center, newhscale=newhscale, newvscale=newvscale, plotRot=False)
            symImg += newImg

        symImg /= nfold
        
        d_sym = nData(symImg)
        d_sym.updateAx('x', newX, d.unit['x'])
        d_sym.updateAx('y', newY, d.unit['y'])
        if plotSym:
            xx, yy = np.meshgrid(xScale, yScale)
            newXX, newYY = np.meshgrid(newX, newY)
            
            fig, ax = plt.subplots(1,2)
            ax[0].pcolormesh(xx, yy, img)
            ax[0].set_aspect(1)
            ax[0].set_title('Before')

            ax[1].pcolormesh(newXX, newYY, symImg)
            ax[1].set_aspect(1)
            ax[1].set_title('{}-fold symmetric'.format(nfold))

            fig.tight_layout()          
    else:
        print('Warning: {}-fold symmetry is invalid.'.format(nfold))
        d_sym = d
    return d_sym