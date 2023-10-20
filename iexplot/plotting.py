
import numpy as np
import matplotlib.pyplot as plt
from math import *


########################################################################
def find_closest(x, x_val):
    """
    returns index, value of an x which is closest to x_val
        x = np.array
        x_val = value for which you are looking
    
    Usage:
        i,x0 = find_closest(xdata,np.mean(xdata)); point closest to the mean
    """
    index = np.absolute(x_val-x).argmin()
    value = x[index]
    return index, value

########################################################################    
""" useful plotting routines """
########################################################################

def plot_1D(x,y,**kwargs):
    """
    x / y 1D numpy arrays 
    **kwargs
        xrange=[x_first,x_last] to plot subrange 
        Norm2One: True/False to normalize graph between zero and one
        offset: y -= offset 
        offset_mean_index: y -= np.mean(y[scale_mean_index[0]:scale_mean_index[-1]])
        scale: y *= scale
        scale_mean_index: y /= np.mean(y[scale_mean_index[0]:scale_mean_index[-1]])
        offset_x: x += offset_x 
        scale_x: x *= scale_x
    """
    kwargs.setdefault('Norm2One',False)
    kwargs.setdefault("offset",0)
    kwargs.setdefault("offset_mean_index",None)
    kwargs.setdefault("scale",1)             
    kwargs.setdefault('scale_mean_index',None) 
    kwargs.setdefault("offset_x",0)
    kwargs.setdefault("scale_x",1)

    if 'xrange' in kwargs:
        first_index, first_value = find_closest(x,kwargs['xrange'][0])
        last_index, last_falue   = find_closest(x,kwargs['xrange'][1])
        x = x[first_index:last_index]
        y = y[first_index:last_index]
        kwargs.pop('xrange')

    if kwargs['Norm2One']:
        y=(y-min(y))/(max(y)-min(y))

    #offset and scaling
    scale=kwargs['scale']
    offset=kwargs['offset']
    
    if kwargs['scale_mean_index'] is not None: 
        scale_mean_index=kwargs['scale_mean_index']
        scale /= np.mean(y[scale_mean_index[0]:scale_mean_index[-1]])
    del kwargs['scale_mean_index']
    
    if kwargs['offset_mean_index'] is not None: 
        offset_mean_index=kwargs['offset_mean_index']
        offset += np.mean(y[offset_mean_index[0]:offset_mean_index[-1]])
    del kwargs['offset_mean_index']
    

    y=y*scale-offset
    x=x*kwargs["scale_x"]+kwargs["offset_x"]

    #remove nonstandard kwargs
    for key in ["Norm2One","offset","scale","offset_x","scale_x"]:
        del kwargs[key]

    if 'xlabel' in kwargs:
        plt.xlabel(kwargs['xlabel'])
        del kwargs['xlabel']
    if 'ylabel' in kwargs:
        plt.ylabel(kwargs['ylabel'])
        del kwargs['ylabel']

    plt.plot(x,y,**kwargs)

def plot_2D(img,scales,units,**kwargs):
    """
    img = 2D numpy array (y,x)
    scales = [yscale,xscale]
    units = [yunit,xunit]
    **kwargs = pcolormesh keywords
        kwargs.setdefault('shading','auto')
    """
    kwargs.setdefault('shading','auto')

    yscale,xscale = scales
    yunit,xunit = units

    plt.pcolormesh(xscale, yscale, img, **kwargs)
    plt.xlabel(xunit)
    plt.ylabel(yunit)

def reduce2d(x,y, **kwargs):
    """
    takes the 2D arrays, x and y and reduces them to 1D arrays removes column/row form kwargs
    **kwargs:
        column
        row
    """
    if "row" in kwargs:
        x=x[kwargs['row'],:]
        y=y[kwargs['row'],:] 
        del kwargs['row']
            
    if "column" in kwargs:
        x=x[:,kwargs['column']]
        y=y[:,kwargs['column']] 
        del kwargs['column']
    return x,y,kwargs

def plot_dimage(dataArray,scaleArray,unitArray, **kwargs):
    """
    dataArray is a 3D np.array(data[y][x]) => images are row by column data
    scaleArray = (scaleY,scaleX) 
    unitArray = (unitY,unitX);  unitX = xlabel
    
    **kwargs
        dim2 = second axis for plotting (default: 'y') => vertical in image
        xCen = cursor x value (default: np.nan => puts in the middle)
        xWidthPix = number of pixels to bin in x
        yCen = cursor y value (default: np.nan => puts in the middle)
        yWidthPix = number of pixels to bin in y
        cmap = colormap ('BuPu'=default)

    returns a dictionary of the images and profiles where
        dictionary={'images':(image,imageH,imageV),'profiles':(profileH,profileV,profileD),'scales':scales}
           image(scale[0],scale[1])
           profileH(scale[1])
           profileV(scale[0])

       

    """
    kwargs.setdefault('dim2','y')
    kwargs.setdefault('xCen',np.nan)
    kwargs.setdefault('xWidthPix',0)
    kwargs.setdefault('yCen',np.nan)
    kwargs.setdefault('yWidthPix',0)
    kwargs.setdefault('cmap','BuPu')
    kwargs.setdefault('shading','auto')
    kwargs.setdefault('debug',False)
       
    datakwargs=['ax','xCen','xWidthPix','yCen','yWidthPix','debug','dim2']
    pltkeys=[key for key in kwargs if key not in datakwargs]
    pltkwargs={key:kwargs[key] for key in pltkeys}
   
    yScale,xScale = scaleArray
    yUnit,xUnit = unitArray
    
    xWidthPix=kwargs['xWidthPix']
    yWidthPix=kwargs['yWidthPix']

    xCenPix = len(xScale)//2 if np.isnan(kwargs['xCen']) else np.abs(xScale - kwargs['xCen']).argmin()
    yCenPix = len(yScale)//2 if np.isnan(kwargs['yCen']) else np.abs(yScale - kwargs['yCen']).argmin()
    
    if kwargs['debug']:
        print(dataArray.shape)
    
    #transform data based on dim2 
    img = dataArray
    cenPix=(yCenPix,xCenPix) #x=1,y=0
    widthPix=(yWidthPix,xWidthPix)
    scales=(yScale,xScale)
    units=(yUnit,xUnit)
    
    #data array y=0,x=1,z=2
    if kwargs['dim2'].lower()=='x': 
        img=np.transpose(dataArray,(1,0))
        cenPix=(xCenPix,yCenPix) 
        widthPix=(xWidthPix,yWidthPix)
        scales=(xScale,yScale)
        units=(xUnit,yUnit)
            
    if kwargs['debug']:
        print('units',cenPix)
        print('cenPix',cenPix)
        print('widthPix',cenPix)
        
    # Image: main image img[y][x][z]
    image = img
    
    #profiles
    profileH = np.nansum(image[cenPix[0]-widthPix[0]:cenPix[0]+max(widthPix[0],1), : ],axis=0)
    profileV = np.nansum(image[:,cenPix[1]-widthPix[1]:cenPix[1]+max(widthPix[1],1)  ],axis=1)
    
    if kwargs['debug']:
        return image,profileH,profileV,cenPix,widthPix

    # Plotting fig
    fig = plt.figure(figsize=(5,5))
    gs = fig.add_gridspec(3, 3)
    
    cursors=True
    #cursors=False
    #plotting main image
    ax1 = fig.add_subplot(gs[1:, :-1])
    scaleMesh = np.meshgrid(scales[1], scales[0])
    im1 = ax1.pcolormesh(scaleMesh[0], scaleMesh[1],image,**pltkwargs)
    ax1.set_xlabel(units[1]) 
    ax1.set_ylabel(units[0])  
    if cursors:
        #plotting main image cursors-horizontal
        ax1.plot(scales[1],np.ones(len(scales[1]))*scales[0][cenPix[0]], color='b', linewidth=0.5) 
        if widthPix[0]>0:
            ax1.plot(scales[1], np.ones(len(scales[1]))*scales[0][cenPix[0]-widthPix[0]], color='b', linewidth=0.5, linestyle='dashed')
            ax1.plot(scales[1], np.ones(len(scales[1]))*scales[0][cenPix[0]+widthPix[0]], color='b', linewidth=0.5, linestyle='dashed')
        #plotting main image cursors-vertical
        ax1.plot(np.ones(len(scales[0]))*scales[1][cenPix[1]],scales[0],color='r', linewidth=0.5) 
        if widthPix[1]>0:
            ax1.plot(np.ones(len(scales[0]))*scales[1][cenPix[1]-widthPix[1]], scales[0], color='r', linewidth=0.5, linestyle='dashed')
            ax1.plot(np.ones(len(scales[0]))*scales[1][cenPix[1]+widthPix[1]], scales[0], color='r', linewidth=0.5, linestyle='dashed')

    plot=True
    if plot:
        #H-profile
        ax2 = fig.add_subplot(gs[0, :-1], sharex=ax1)
        ax2.plot(scales[1], profileH, 'b-')
        y1, y2 = ax2.get_ylim()
        if cursors:
            ax2.plot(np.ones(2)*scales[1][cenPix[1]],np.array([y1, y2]), color='r', linewidth=0.5)
            if widthPix[1]>0:
                ax2.plot(np.ones(2)*scales[1][cenPix[1]-widthPix[1]],np.array([y1, y2]), color='r', linewidth=0.5, linestyle='dashed')
                ax2.plot(np.ones(2)*scales[1][cenPix[1]+widthPix[1]],np.array([y1, y2]), color='r', linewidth=0.5, linestyle='dashed')
        ax2.xaxis.set_visible(False)    

    plot=True
    if plot:
        #V-profile
        ax3 = fig.add_subplot(gs[1:, -1], sharey=ax1)
        ax3.plot(profileV, scales[0],'r-')
        x1, x2 = ax3.get_xlim()
        if cursors:
            ax3.plot(np.array([x1, x2]), np.ones(2)*scales[0][cenPix[0]], color='b', linewidth=0.5)
            if widthPix[0]>0:
                ax3.plot(np.array([x1, x2]), np.ones(2)*scales[0][cenPix[0]-widthPix[0]], color='b', linewidth=0.5, linestyle='dashed')
                ax3.plot(np.array([x1, x2]), np.ones(2)*scales[0][cenPix[0]+widthPix[0]], color='b', linewidth=0.5, linestyle='dashed')
        ax3.yaxis.set_visible(False)

    plt.show()
    return {'images':(image),'profiles':(profileH,profileV),'scales':scales}

def plot_3D(dataArray,scaleArray,unitArray, **kwargs):
    """
    dataArray is a 3D np.array(data[y][x][z]) => images are row by column data, which are then stacked (np.dstack)
    scaleArray = (scaleY,scaleX,scaleZ) 
    unitArray = (unitY,unitX,unitZ);  unitX = xlabel
    
    **kwargs
        dim3 = third axis for plotting (default: 'z')
        dim2 = second axis for plotting (default: 'y') => vertical in main image
        xCen = cursor x value (default: np.nan => puts in the middle)
        xWidthPix = number of pixels to bin in x
        yCen = cursor y value (default: np.nan => puts in the middle)
        yWidthPix = number of pixels to bin in y
        zCen = cursor y value (default: np.nan => puts in the middle)
        zWidthPix = number of pixels to bin in y
        cmap = colormap ('BuPu'=default)

    returns a dictionary of the images and profiles where
        dictionary={'images':(image,imageH,imageV),'profiles':(profileH,profileV,profileD),'scales':scales}
           image(scale[0],scale[1])
           imageH(scale[0],scale[2])
           imageV(scale[1],scale[2])
           profileH(scale[1])
           profileV(scale[0])
           profileD(scale[2])
       

    """
    kwargs.setdefault('dim2','y')
    kwargs.setdefault('dim3','z')
    kwargs.setdefault('xCen',np.nan)
    kwargs.setdefault('xWidthPix',0)
    kwargs.setdefault('yCen',np.nan)
    kwargs.setdefault('yWidthPix',0)
    kwargs.setdefault('zCen',np.nan)
    kwargs.setdefault('zWidthPix',0)
    kwargs.setdefault('cmap','BuPu')
    kwargs.setdefault('shading','auto')
    kwargs.setdefault('debug',False)
       
    datakwargs=['ax','xCen','xWidthPix','yCen','yWidthPix','zCen','zWidthPix','debug','dim3','dim2']
    pltkeys=[key for key in kwargs if key not in datakwargs]
    pltkwargs={key:kwargs[key] for key in pltkeys}
   
    yScale,xScale,zScale = scaleArray
    yUnit,xUnit,zUnit = unitArray
    
    xWidthPix=kwargs['xWidthPix']
    yWidthPix=kwargs['yWidthPix']
    zWidthPix=kwargs['zWidthPix']

    xCenPix = len(xScale)//2 if np.isnan(kwargs['xCen']) else np.abs(xScale - kwargs['xCen']).argmin()
    yCenPix = len(yScale)//2 if np.isnan(kwargs['yCen']) else np.abs(yScale - kwargs['yCen']).argmin()
    zCenPix = len(zScale)//2 if np.isnan(kwargs['zCen']) else np.abs(zScale - kwargs['zCen']).argmin()
    
    if kwargs['debug']:
        print(dataArray.shape)
    
    #transform data based on dim3 and dim2 
    img = dataArray
    cenPix=(yCenPix,xCenPix,zCenPix) #x=1,y=0,z=2
    widthPix=(yWidthPix,xWidthPix,zWidthPix)
    scales=(yScale,xScale,zScale)
    units=(yUnit,xUnit,zUnit)
    
    #data array y=0,x=1,z=2
    if kwargs['dim3'].lower()=='z':             
        if kwargs['dim2'].lower()=='x': 
            img=np.transpose(dataArray,(1,0,2))
            cenPix=(xCenPix,yCenPix,zCenPix) 
            widthPix=(xWidthPix,yWidthPix,zWidthPix)
            scales=(xScale,yScale,zScale)
            units=(xUnit,yUnit,zUnit)

            
    elif kwargs['dim3'].lower()=='y':
        if kwargs['dim2'].lower()=='z':
            img=np.transpose(dataArray,(1,2,0))#data array y=0,x=1,z=2
            cenPix=(xCenPix,zCenPix,yCenPix) 
            widthPix=(xWidthPix,zWidthPix,yWidthPix)
            scales=(xScale,zScale,yScale)
            units=(xUnit,zUnit,yUnit)
        else:
            img=np.transpose(dataArray,(2,1,0))#data array y=0,x=1,z=2
            cenPix=(zCenPix,xCenPix,yCenPix) 
            widthPix=(zWidthPix,xWidthPix,yWidthPix)
            scales=(zScale,xScale,yScale)
            units=(zUnit,xUnit,yUnit)
            
    elif kwargs['dim3'].lower()=='x':
        if kwargs['dim2'].lower()=='z':
            img=np.transpose(dataArray,(0,2,1))#data array y=0,x=1,z=2
            cenPix=(yCenPix,zCenPix,xCenPix) 
            widthPix=(yWidthPix,zWidthPix,xWidthPix)
            scales=(yScale,zScale,xScale)
            units=(yUnit,zUnit,xUnit)
        else:
            img=np.transpose(dataArray,(2,0,1))#data array y=0,x=1,z=2
            cenPix=(zCenPix,yCenPix,xCenPix) 
            widthPix=(zWidthPix,yWidthPix,xWidthPix)
            scales=(zScale,yScale,xScale)
            units=(zUnit,yUnit,xUnit)
            
    if kwargs['debug']:
        print('units',cenPix)
        print('cenPix',cenPix)
        print('widthPix',cenPix)
        
    # Image: main image img[y][x][z]
    image = np.nansum(img[:,:,cenPix[2]-widthPix[2]:cenPix[2]+max(widthPix[2],1)    ],axis=2) #yx
    imageV = np.nansum(img[:, cenPix[1]-widthPix[1]:cenPix[1]+max(widthPix[1],1),:  ],axis=1) #yz
    imageH = np.nansum(img[   cenPix[0]-widthPix[1]:cenPix[0]+max(widthPix[0],1):,:,],axis=0) #xz
    
    #profiles
    profileH = np.nansum(image[cenPix[0]-widthPix[0]:cenPix[0]+max(widthPix[0],1), : ],axis=0)
    profileV = np.nansum(image[:,cenPix[1]-widthPix[1]:cenPix[1]+max(widthPix[1],1)  ],axis=1)
    profileD = np.nansum(imageV[cenPix[0]-widthPix[0]:cenPix[0]+max(widthPix[0],1),:],axis=0)
    
    if kwargs['debug']:
        return img,image,imageV,imageH, profileH,profileV,profileD,cenPix,widthPix

    # Plotting fig
    fig = plt.figure(figsize=(5,5))
    gs = fig.add_gridspec(4, 4)
    
    cursors=True
    #cursors=False
    #plotting main image
    ax1 = fig.add_subplot(gs[2:4, 0:2])
    scaleMesh = np.meshgrid(scales[1], scales[0])
    im1 = ax1.pcolormesh(scaleMesh[0], scaleMesh[1],image,**pltkwargs)
    ax1.set_xlabel(units[1]) 
    ax1.set_ylabel(units[0])  
    if cursors:
        #plotting main image cursors-horizontal
        ax1.plot(scales[1],np.ones(len(scales[1]))*scales[0][cenPix[0]], color='b', linewidth=0.5) 
        if widthPix[0]>0:
            ax1.plot(scales[1], np.ones(len(scales[1]))*scales[0][cenPix[0]-widthPix[0]], color='b', linewidth=0.5, linestyle='dashed')
            ax1.plot(scales[1], np.ones(len(scales[1]))*scales[0][cenPix[0]+widthPix[0]], color='b', linewidth=0.5, linestyle='dashed')
        #plotting main image cursors-vertical
        ax1.plot(np.ones(len(scales[0]))*scales[1][cenPix[1]],scales[0],color='r', linewidth=0.5) 
        if widthPix[1]>0:
            ax1.plot(np.ones(len(scales[0]))*scales[1][cenPix[1]-widthPix[1]], scales[0], color='r', linewidth=0.5, linestyle='dashed')
            ax1.plot(np.ones(len(scales[0]))*scales[1][cenPix[1]+widthPix[1]], scales[0], color='r', linewidth=0.5, linestyle='dashed')

    plot=True
    if plot:
        #plotting imageV
        ax4 = fig.add_subplot(gs[2:4, 2:3])
        scaleMesh = np.meshgrid(scales[2], scales[0])
        im4 = ax4.pcolormesh(scaleMesh[0], scaleMesh[1], imageV,**pltkwargs)        
        ax4.set_xlabel(units[2]) 
        ax4.set_ylabel(units[0]) 
        ax4.yaxis.set_visible(False)
        if cursors:
        #plotting imageV cursors-horizontal
            ax4.plot(np.ones(len(scales[0]))*scales[2][cenPix[2]],scales[0], color='g', linewidth=0.5)
            if widthPix[2]>0:
                ax4.plot(np.ones(len(scales[0]))*scales[2][cenPix[2]-widthPix[2]],scales[0], color='g', linewidth=0.5, linestyle='dashed')
                ax4.plot(np.ones(len(scales[0]))*scales[2][cenPix[2]+widthPix[2]],scales[0], color='g', linewidth=0.5, linestyle='dashed')
            #plotting imageV cursors-vertical
            ax4.plot(scales[2],np.ones(len(scales[2]))*scales[0][cenPix[0]], color='b', linewidth=0.5)
            if widthPix[0]>0:
                ax4.plot(scales[2],np.ones(len(scales[2]))*scales[0][cenPix[0]-widthPix[0]], color='b', linewidth=0.5, linestyle='dashed')
                ax4.plot(scales[2],np.ones(len(scales[2]))*scales[0][cenPix[0]+widthPix[0]], color='b', linewidth=0.5, linestyle='dashed')

    plot=True
    if plot:
        #plotting imageH
        ax5 = fig.add_subplot(gs[1:2, 0:2])
        scaleMesh = np.meshgrid(scales[1], scales[2]) 
        im5 = ax5.pcolormesh(scaleMesh[0], scaleMesh[1], np.transpose(imageH),**pltkwargs)
        ax5.set_xlabel(units[1]) 
        ax5.set_ylabel(units[2]) 
        ax5.xaxis.set_visible(False)
        if cursors:
            #plotting imageH cursors-horizontal
            ax5.plot(scales[1],np.ones(len(scales[1]))*scales[2][cenPix[2]], color='g', linewidth=0.5)
            if widthPix[2]>0:
                ax5.plot(scales[1],np.ones(len(scales[1]))*scales[2][cenPix[2]-widthPix[2]], color='g', linewidth=0.5, linestyle='dashed')
                ax5.plot(scales[1],np.ones(len(scales[1]))*scales[2][cenPix[2]+widthPix[2]], color='g', linewidth=0.5, linestyle='dashed')
            #plotting imageH cursors-vertical
            ax5.plot(np.ones(len(scales[2]))*scales[1][cenPix[1]],scales[2], color='b', linewidth=0.5) #vertical
            if widthPix[1]>0:
                ax5.plot(np.ones(len(scales[2]))*scales[1][cenPix[1]-widthPix[1]],scales[2], color='b', linewidth=0.5, linestyle='dashed')
                ax5.plot(np.ones(len(scales[2]))*scales[1][cenPix[1]+widthPix[1]],scales[2], color='b', linewidth=0.5, linestyle='dashed')

    plot=True
    if plot:
        #H-profile
        ax2 = fig.add_subplot(gs[0, 0:2], sharex=ax1)
        ax2.plot(scales[1], profileH, 'b-')
        y1, y2 = ax2.get_ylim()
        if cursors:
            ax2.plot(np.ones(2)*scales[1][cenPix[1]],np.array([y1, y2]), color='r', linewidth=0.5)
            if widthPix[1]>0:
                ax2.plot(np.ones(2)*scales[1][cenPix[1]-widthPix[1]],np.array([y1, y2]), color='r', linewidth=0.5, linestyle='dashed')
                ax2.plot(np.ones(2)*scales[1][cenPix[1]+widthPix[1]],np.array([y1, y2]), color='r', linewidth=0.5, linestyle='dashed')
        ax2.xaxis.set_visible(False)    

    plot=True
    if plot:
        #V-profile
        ax3 = fig.add_subplot(gs[2:4, -1], sharey=ax1)
        ax3.plot(profileV, scales[0],'r-')
        x1, x2 = ax3.get_xlim()
        if cursors:
            ax3.plot(np.array([x1, x2]), np.ones(2)*scales[0][cenPix[0]], color='b', linewidth=0.5)
            if widthPix[0]>0:
                ax3.plot(np.array([x1, x2]), np.ones(2)*scales[0][cenPix[0]-widthPix[0]], color='b', linewidth=0.5, linestyle='dashed')
                ax3.plot(np.array([x1, x2]), np.ones(2)*scales[0][cenPix[0]+widthPix[0]], color='b', linewidth=0.5, linestyle='dashed')
        ax3.yaxis.set_visible(False)

    plot=True
    if plot:
        #z-profile
        ax6 = fig.add_subplot(gs[0:2, 2:4])
        ax6.plot(scales[2],profileD,'g-')
        y1, y2 = ax6.get_ylim()
        if cursors:
            ax6.plot(np.ones(2)*scales[2][cenPix[2]], np.array([y1, y2]), color='k', linewidth=0.5)
            if widthPix[2]>0:
                ax6.plot(np.ones(2)*scales[2][cenPix[2]-widthPix[2]], np.array([y1, y2]), color='k', linewidth=0.5, linestyle='dashed')
                ax6.plot(np.ones(2)*scales[2][cenPix[2]+max(widthPix[2],1)], np.array([y1, y2]), color='k', linewidth=0.5, linestyle='dashed')

        ax6.yaxis.set_label_position("right")
        ax6.yaxis.tick_right()
        ax6.xaxis.set_label_position("top")
        ax6.xaxis.tick_top()
        ax6.set_xlabel(units[2]) 

    #return {'images':(image,imageH,imageV),'profiles':(profileH,profileV,profileD),'scales':scales}

def plot_ra(ra,**kwargs):
    dataArray=ra.data.data
    scaleArray=tuple(ra.data.coords[key].data for key in dict(ra.data.coords).keys())
    unitArray=tuple(dict(ra.data.coords).keys())
    
    if len(ra.data.data.shape)==2:
        plot_dimage(dataArray,scaleArray,unitArray, **kwargs)
    elif len(ra.data.data.shape)==3:
        plot_3D(dataArray,scaleArray,unitArray, **kwargs)

def colormap_colors(i,size,cmap_name,**kwargs):
    """
    Used to get a color from a color map, return color for 
    i: the index of the color
    size: how many gradations
    cmap_name: python color map  'rainbow','rainbow-r','turbo','coolwarm','tab20b',Blues' 
        For list see: https://matplotlib.org/stable/tutorials/colors/colormaps.html
        Note: plt.cm.cmap_name will show color map
    **kwargs:
        gamma: gamma for non linear colormaps

    Usage: 
        detNum = 33
        scanList = list(range(250,261,1))
        for scanNum in scanList:
            plot_mda(scanNum,detNum,color=colormap_colors(i,len(scanList),'coolwarm'))
    """
    if hasattr(plt.cm,cmap_name):
        cm = getattr(plt.cm,cmap_name)
        if 'gamma' in kwargs:
            colors = cm(np.linspace(0,1,size)**kwargs['gamma'])
        else:
            colors = cm(np.linspace(0,1,size))
        return colors[i]
    else:
        print('\n Not a valid color map, see https://matplotlib.org/stable/tutorials/colors/colormaps.html')
        return None
    

