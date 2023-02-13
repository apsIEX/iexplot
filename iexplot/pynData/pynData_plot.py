import matplotlib.pyplot as plt 

from iexplot.pynData.pynData import *
from iexplot.plotting import plot_1D,plot_2D
#==============================================================================
# Utils for plotting and slicing
#==============================================================================

def niceplot(*ds):
    '''
    Simple plot for 1D and 2D nData
    *ds pnData files
    '''
    plt.figure()
    d=ds[0]
    try:
        dim = len(d.data.shape)
        for d in list(ds):
            if dim==1:
                if(d.data.shape[0]<2):
                    print("Data is a single point "+str(d.data))
                else:
                    x = d.scale['x']
                    y = d.data
                    plot_1D(x,y,xlabel=d.unit['x'],ylabel=d.unit['y'])
                    
            elif dim==2:
                img = d.data
                scales = [d.scale['y'],d.scale['x']]
                units = [d.unit['y'],d.unit['x']]
                plot_2D(img,scales,units)
            elif dim>2:
                print('Warning: niceplot can only plot 1d and 2d data.')
    except:
            print('Note a valid object')
    plt.show()


def niceplot_avg(d,ax='y',Cen=np.nan,WidthPix=np.nan):
    """
    bins 2D data in ax, with Center, and WidthPix 
    if Center=np.nan then center is the midpoint
    if WidthPix=np.nan then whole image is binned    
    """
    if(len(d.data.shape)==2):
        Scale=d.scale[ax]
        if np.isnan(Cen):
            CenPix = len(Scale)//2
        else:
            CenPix = np.argmin((Scale-Cen)**2)
        if np.isnan(WidthPix):
            WidthPix=len(Scale)//2

        if(ax is 'x'):
            img_avg = np.nansum(d.data[:,CenPix-WidthPix:CenPix+WidthPix], axis=1)
            bx='y'
        elif(ax is 'y'):
            img_avg = np.nansum(d.data[CenPix-WidthPix:CenPix+WidthPix,:], axis=0)
            bx='x'
        avg=nData(img_avg)
        avg.updateAx('x', d.scale[bx], d.unit[bx])
        niceplot(avg)
        
    else:
        print('only works for 2D data')


def plot2D_old(d, xCen=np.nan, xWidthPix=0, yCen=np.nan, yWidthPix=0, vmin=np.nan, vmax=np.nan):
	'''
	d:          nData instance with xScale: dim1 and yScale: dim0
	xCen: vertical cursor x position
	xWidthPix: with for binning in x-direction
	yCen: horizontal cursor y position
	yWidthPix: with for binning in y-direction
	vmin: color scale min; default = np.nan uses the data to set
	vmax: color scale max; default = np.nan uses the data to set
	'''
	img = d.data
	xScale = d.scale['x']
	xUnit = d.unit['x']
	yScale = d.scale['y']
	yUnit = d.unit['y']

	if np.isnan(xCen):
		xCenPix = len(xScale)//2
	else:
		xCenPix = np.argmin((xScale-xCen)**2)

	if np.isnan(yCen):
		yCenPix = len(yScale)//2
	else:
		yCenPix = np.argmin((yScale-yCen)**2)

	print(xCenPix)

	# Cut at y
	if yWidthPix>0:
		yCut = np.nansum(img[yCenPix-yWidthPix:yCenPix+yWidthPix,:], axis=0)
	else:
		yCut = img[yCenPix,:]

	# Cut at x
	if xWidthPix>0:
		xCut = np.nansum(img[:,xCenPix-xWidthPix:xCenPix+xWidthPix], axis=1)
	else:
		xCut = img[:,xCenPix]

	# Set scales
	if np.isnan(vmin):
		vmin = np.nanpercentile(img, 5)
	if np.isnan(vmax):
		vmax = np.nanpercentile(img, 95)

	# Generating plots
	xyScale = np.meshgrid(xScale, yScale)

	fig = plt.figure(figsize=(5,5))
	gs = fig.add_gridspec(3, 3)

	ax1 = fig.add_subplot(gs[1:, :-1])
	im1 = ax1.pcolormesh(xyScale[0], xyScale[1], img, vmin=vmin, vmax=vmax,shading='auto')
	ax1.set_xlabel(xUnit) # The line will do nothing if xUnit==''
	ax1.set_ylabel(yUnit)

	ax1.plot(xScale, np.ones(len(xScale))*yScale[yCenPix], color='r', linewidth=0.5)
	ax1.plot(np.ones(len(yScale))*xScale[xCenPix], yScale, color='b', linewidth=0.5)
	if xWidthPix>0:
		ax1.plot(np.ones(len(yScale))*xScale[xCenPix-xWidthPix], yScale, color='b', linewidth=0.5)
		ax1.plot(np.ones(len(yScale))*xScale[xCenPix+xWidthPix], yScale, color='b', linewidth=0.5)
	if yWidthPix>0:
		ax1.plot(xScale, np.ones(len(xScale))*yScale[yCenPix-yWidthPix], color='r', linewidth=0.5)
		ax1.plot(xScale, np.ones(len(xScale))*yScale[yCenPix+yWidthPix], color='r', linewidth=0.5)

	ax2 = fig.add_subplot(gs[0, :-1], sharex=ax1)
	ax2.plot(xScale, yCut, 'r-')
	y1, y2 = ax2.get_ylim()
	ax2.plot(np.array([xScale[xCenPix],xScale[xCenPix]]), np.array([y1, y2]), color='b', linewidth=0.5)
	if xWidthPix>0:
		ax2.plot(np.array([xScale[xCenPix-xWidthPix],xScale[xCenPix-xWidthPix]]), np.array([y1, y2]), 
				 color='b', linewidth=0.5)
		ax2.plot(np.array([xScale[xCenPix+xWidthPix],xScale[xCenPix+xWidthPix]]), np.array([y1, y2]), 
				 color='b', linewidth=0.5)
	ax2.xaxis.set_visible(False)

	ax3 = fig.add_subplot(gs[1:, -1], sharey=ax1)
	ax3.plot(xCut, yScale,'b-')
	x1, x2 = ax3.get_xlim()
	ax3.plot(np.array([x1, x2]), np.array([yScale[yCenPix],yScale[yCenPix]]), color='r', linewidth=0.5)
	if yWidthPix>0:
		ax3.plot(np.array([x1, x2]), np.array([yScale[yCenPix-yWidthPix],yScale[yCenPix-yWidthPix]]), 
				 color='r', linewidth=0.5)
		ax3.plot(np.array([x1, x2]), np.array([yScale[yCenPix+yWidthPix],yScale[yCenPix+yWidthPix]]), 
				 color='r', linewidth=0.5)

	ax3.yaxis.set_visible(False)

	cb_ax = fig.add_axes([0.95, 0.1, 0.02, 0.8])
	cbar = fig.colorbar(im1, cax=cb_ax, fraction=.1)

	xCut = nData(xCut)
	xCut.updateAx('x', yScale, yUnit)

	yCut = nData(yCut)
	yCut.updateAx('x', xScale, xUnit)
	return xCut, yCut

####################################################################################################
def Compare2D(d1,d2,**kwargs): #JM added
	"""
	d1: first nData, d2:second nData
	red/blue image1 (top); magenta/green image2 (bottom)
	kwargs:
		xCen=np.nan, position of vertical cursor
		xWidthPix=0, number x to bin
		yCen=np.nan, positon of horizontal cursor
		yWidthPix=0, number y pixels to bin
		intScale=1, adjust the intensity scaling of d2
		vmin=np.nan, for d1 color table (use intScale to modify d2)
		vmax=np.nan, for d1 color table (use intScale to modify d2)
		
		xOffset=0, offset the vertical cut of d2, in pixels
		yOffset=0, offset the horizaional cut of d2, in pixels
		
		csr = 'on', to turn off the cursors set csr = None
	"""

	args={
		'xCen':np.nan,
		'xWidthPix':0,
		'yCen':np.nan,
		'yWidthPix':0,
		'vmin':np.nan, 
		'vmax':np.nan,
		'intScale':1,
		'xOffsetPix':0,
		'yOffsetPix':0,
		'csr':'on',
	}
	args.update(kwargs)

	xOffsetPix = args['xOffsetPix']
	yOffsetPix = args['yOffsetPix']

	img1 = d1.data
	x1Scale = d1.scale['x']
	x1Unit = d1.unit['x']
	y1Scale = d1.scale['y']
	y2Unit = d2.unit['y']

	xmin=xOffsetPix; xmax=d2.data.shape[1]+xOffsetPix
	ymin=yOffsetPix; ymax=d2.data.shape[0]+yOffsetPix
	img2 = d2.data[ymin:ymax,xmin:xmax]
	img2=np.pad(img2,((min(yOffsetPix,0), max(yOffsetPix,0)), (min(xOffsetPix,0), max(xOffsetPix,0))),mode='constant')

	x2Scale = d2.scale['x']
	x2Unit = d2.unit['x']
	y2Scale = d2.scale['y']
	y1Unit = d1.unit['y']

	if np.isnan(args['xCen']):
		xCen = np.median(x1Scale)
	else:
		xCen = args['xCen']
	x1CenPix = np.argmin((x1Scale-xCen)**2)
	x2CenPix = np.argmin((x2Scale-xCen)**2)
	
	if np.isnan(args['yCen']):
		yCen = np.median(y1Scale)
	else:
		yCen = args['yCen']
	y1CenPix = np.argmin((y1Scale-yCen)**2)
	y2CenPix = np.argmin((y2Scale-yCen)**2)

	intScale=args['intScale']
	
	# Cut at y
	yWidthPix=args['yWidthPix']

	if yWidthPix>0:
		y1Cut = np.nansum(img1[y1CenPix-yWidthPix:y1CenPix+yWidthPix,:], axis=0)
		y2Cut = np.nansum(img2[y2CenPix-yWidthPix+0:y2CenPix+yWidthPix+0,:], axis=0)
	else:
		y1Cut = img1[y1CenPix,:]
		y2Cut = img2[y2CenPix+0,:]
	y2Cut*=intScale

	# Cut at x
	xWidthPix=args['xWidthPix']
	if xWidthPix>0:
		x1Cut = np.nansum(img1[:,x1CenPix-xWidthPix:x1CenPix+xWidthPix], axis=1)
		x2Cut = np.nansum(img2[:,x2CenPix+0-xWidthPix:x2CenPix+xWidthPix+0], axis=1)

	else:
		x1Cut = img1[:,x1CenPix]
		x2Cut = img2[:,x2CenPix+0]
		#x2Cut = x1Cut#img2[:,x2CenPix]
	x2Cut*=intScale

	# --------Set color scale image1
	if np.isnan(args['vmin']):
		vmin = np.nanpercentile(img1, 5)
	else:
		vmin=args['vmin']
	if np.isnan(args['vmax']):
		vmax = np.nanpercentile(img1, 95)
	else:
		vmax=args['vmax']
   
	# --------Generating plots--------
	fig = plt.figure(figsize=(10,10))
	gs = fig.add_gridspec(5, 3)
	xyScale = np.meshgrid(x1Scale, y1Scale)
	csr = args['csr']

	###--------image1--------
	ax1 = fig.add_subplot(gs[1:3, 0:2])
	im1 = ax1.pcolormesh(xyScale[0], xyScale[1], img1, vmin=vmin, vmax=vmax)
	ax1.set_xlabel(x1Unit) # The line will do nothing if xUnit==''
	ax1.set_ylabel(y2Unit)
	# adding cursors
	if csr is not None:
		ax1.plot(x1Scale, np.ones(len(x1Scale))*y1Scale[y1CenPix], color='r', linewidth=0.5)
		ax1.plot(np.ones(len(y1Scale))*x1Scale[x1CenPix], y1Scale, color='b', linewidth=0.5)
		if xWidthPix>0:
			ax1.plot(np.ones(len(y1Scale))*x1Scale[x1CenPix-xWidthPix], y1Scale, color='b', linewidth=0.5) #(-)
			ax1.plot(np.ones(len(y1Scale))*x1Scale[x1CenPix+xWidthPix], y1Scale, color='b', linewidth=0.5) #(+)
		if yWidthPix>0:
			ax1.plot(x1Scale, np.ones(len(x1Scale))*y1Scale[y1CenPix-yWidthPix], color='r', linewidth=0.5) #(-)
			ax1.plot(x1Scale, np.ones(len(x1Scale))*y1Scale[y1CenPix+yWidthPix], color='r', linewidth=0.5) #(+)

	###--------image2--------
	ax2 = fig.add_subplot(gs[3:5, 0:2])
	im2 = ax2.pcolormesh(xyScale[0], xyScale[1], img2, vmin=vmin/intScale, vmax=vmax/intScale)
	ax2.set_xlabel(x2Unit) # The line will do nothing if xUnit==''
	ax2.set_ylabel(y2Unit)
	#adding cursors
	if csr is not None:
		ax2.plot(x1Scale, np.ones(len(x1Scale))*y1Scale[y1CenPix], color='r', linewidth=0.5)
		ax2.plot(np.ones(len(y1Scale))*x1Scale[x1CenPix], y2Scale, color='b', linewidth=0.5)
		if xWidthPix>0:
			ax2.plot(np.ones(len(y2Scale))*x2Scale[x2CenPix-xWidthPix]+0, y2Scale, color='b', linewidth=0.5) #(-)
			ax2.plot(np.ones(len(y2Scale))*x2Scale[x2CenPix+xWidthPix]+0, y2Scale, color='b', linewidth=0.5) #(3)
		if yWidthPix>0:
			ax2.plot(x2Scale, np.ones(len(x2Scale))*y2Scale[y2CenPix-yWidthPix]+0, color='r', linewidth=0.5) #(-)
			ax2.plot(x2Scale, np.ones(len(x2Scale))*y2Scale[y2CenPix+yWidthPix]+0, color='r', linewidth=0.5) #(+)    

	###--------horizontal profile--------
	ax3 = fig.add_subplot(gs[0, 0:2], sharex=ax1)
	ax3.plot(x1Scale, y1Cut, 'r-')
	ax3.plot(x1Scale, y2Cut, 'm-')
	if csr is not None:
		y1, y2 = ax2.get_ylim()
		ax2.plot(np.array([x1Scale[x1CenPix],x1Scale[x1CenPix]]), np.array([y1, y2]), color='b', linewidth=0.5)
		if xWidthPix>0:
			ax2.plot(np.array([x1Scale[x1CenPix-xWidthPix],x1Scale[x1CenPix-xWidthPix]]), np.array([y1, y2]), 
					 color='b', linewidth=0.5)
	ax2.xaxis.set_visible(False)
    
	###--------vertical profile--------
	ax3 = fig.add_subplot(gs[1:3,2], sharey=ax1)
	ax3.plot(x1Cut, y1Scale,'b-')
	ax3.plot(x2Cut, y2Scale,'g-')
	if csr is not None:
		x1, x2 = ax3.get_xlim()
		ax3.plot(np.array([x1, x2]), np.array([y1Scale[y1CenPix],y1Scale[y1CenPix]]), color='r', linewidth=0.5)
		if yWidthPix>0:
			ax3.plot(np.array([x1, x2]), np.array([y1Scale[y1CenPix-yWidthPix],y1Scale[y1CenPix-yWidthPix]]), 
					 color='r', linewidth=0.5) 
	ax3.yaxis.set_visible(False)
    
	###--------color bar--------
	cb_ax = fig.add_axes([0.95, 0.1, 0.02, 0.8])
	cbar = fig.colorbar(im1, cax=cb_ax, fraction=.1)
	return 
####################################################################################################

def plot3D(d, ax='z', xCen=np.nan, xWidthPix=0, yCen=np.nan, yWidthPix=0, zCen=np.nan, zWidthPix=0):
    '''
    img3D:      3D array.
    xScale:     Dim 2.
    yScale:     Dim 1.
    zScale:     Dim 0.

    Input:
    ax:         Default is 'z'. Along which dimension to show the line cut
    '''
    img3D = d.data
    xScale = d.scale['x']
    xUnit = d.unit['x']
    yScale = d.scale['y']
    yUnit = d.unit['y']
    zScale = d.scale['z']
    zUnit = d.unit['z']

    if np.isnan(xCen):
        xCenPix = len(xScale)//2
    else:
        xCenPix = np.argmin((xScale-xCen)**2)

    if np.isnan(yCen):
        yCenPix = len(yScale)//2
    else:
        yCenPix = np.argmin((yScale-yCen)**2)

    if np.isnan(zCen):
        zCenPix = len(zScale)//2
    else:
        zCenPix = np.argmin((zScale-zCen)**2)
    # Image cut at z
    if zWidthPix>0:
        zImage = np.nansum(img3D[zCenPix-zWidthPix:zCenPix+zWidthPix,:,:], axis=0)
    else:
        zImage = img3D[zCenPix,:,:]

    # Image cut at y
    if yWidthPix>0:
        yImage = np.nansum(img3D[:,yCenPix-yWidthPix:yCenPix+yWidthPix,:], axis=1)
    else:
        yImage = img3D[:,yCenPix,:]

    # Image cut at x
    if xWidthPix>0:
        xImage = np.nansum(img3D[:,:,xCenPix-xWidthPix:xCenPix+xWidthPix], axis=2)
    else:
        xImage = img3D[:,:,xCenPix]

    # Plotting fig
    if ax=='z':
        fig = plt.figure(figsize=(5,5))
        gs = fig.add_gridspec(2, 2)

        ax1 = fig.add_subplot(gs[1, 0])
        xyScale = np.meshgrid(xScale, yScale)
        im1 = ax1.pcolormesh(xyScale[0], xyScale[1], zImage)
        ax1.set_xlabel(xUnit)
        ax1.set_ylabel(yUnit)
        ax1.plot(xScale, np.ones(len(xScale))*yScale[yCenPix], color='r', linewidth=0.5)
        ax1.plot(np.ones(len(yScale))*xScale[xCenPix], yScale, color='b', linewidth=0.5)
        if xWidthPix>0:
            ax1.plot(np.ones(len(yScale))*xScale[xCenPix-xWidthPix], yScale, color='b', linewidth=0.5)
            ax1.plot(np.ones(len(yScale))*xScale[xCenPix+xWidthPix], yScale, color='b', linewidth=0.5)
        if yWidthPix>0:
            ax1.plot(xScale, np.ones(len(xScale))*yScale[yCenPix-yWidthPix], color='r', linewidth=0.5)
            ax1.plot(xScale, np.ones(len(xScale))*yScale[yCenPix+yWidthPix], color='r', linewidth=0.5)

        ax2 = fig.add_subplot(gs[0, 0], sharex=ax1)
        xzScale = np.meshgrid(xScale, zScale)
        im2 = ax2.pcolormesh(xzScale[0], xzScale[1], yImage)
        ax2.xaxis.set_visible(False)
        ax2.set_xlabel(xUnit)
        ax2.set_ylabel(zUnit)
        
        ax3 = fig.add_subplot(gs[1, 1], sharey=ax1)
        zyScale = np.meshgrid(zScale, yScale)
        im3 = ax3.pcolormesh(zyScale[0], zyScale[1], xImage.transpose())
        ax3.yaxis.set_visible(False)
        ax3.set_xlabel(zUnit)
        ax3.set_ylabel(yUnit)

        if yWidthPix>0:
            zCut = np.nansum(xImage[:,yCenPix-yWidthPix:yCenPix+yWidthPix], axis=1)
        else:
            zCut = xImage[:,yCenPix]
        
        ax0 = fig.add_subplot(gs[0, 1], sharex=ax3)
        ax0.yaxis.set_visible(False)
        ax4 = ax0.twinx()
        ax4.plot(zScale, zCut, 'k-')
        z1, z2 = ax4.get_ylim()
        ax4.plot(np.array([zScale[zCenPix],zScale[zCenPix]]), np.array([z1, z2]), color='g', linewidth=0.5)
        if zWidthPix>0:
            ax4.plot(np.array([zScale[zCenPix-zWidthPix],zScale[zCenPix-zWidthPix]]), 
                     np.array([z1, z2]), color='g', linewidth=0.5)
            ax4.plot(np.array([zScale[zCenPix+zWidthPix],zScale[zCenPix+zWidthPix]]), 
                     np.array([z1, z2]), color='g', linewidth=0.5)
        ax4.xaxis.set_visible(False)

        plt.tight_layout()
        
        cut = nData(zCut)
        cut.updateAx('x', zScale, zUnit)
    elif ax=='y':
        fig = plt.figure(figsize=(5,5))
        gs = fig.add_gridspec(2, 2)

        ax1 = fig.add_subplot(gs[1, 0])
        xzScale = np.meshgrid(xScale, zScale)
        im1 = ax1.pcolormesh(xzScale[0], xzScale[1], yImage)
        ax1.set_xlabel(xUnit)
        ax1.set_ylabel(zUnit)
        ax1.plot(xScale, np.ones(len(xScale))*zScale[zCenPix], color='r', linewidth=0.5)
        ax1.plot(np.ones(len(zScale))*xScale[xCenPix], zScale, color='b', linewidth=0.5)
        if xWidthPix>0:
            ax1.plot(np.ones(len(zScale))*xScale[xCenPix-xWidthPix], zScale, color='b', linewidth=0.5)
            ax1.plot(np.ones(len(zScale))*xScale[xCenPix+xWidthPix], zScale, color='b', linewidth=0.5)
        if zWidthPix>0:
            ax1.plot(xScale, np.ones(len(xScale))*zScale[zCenPix-zWidthPix], color='r', linewidth=0.5)
            ax1.plot(xScale, np.ones(len(xScale))*zScale[zCenPix+zWidthPix], color='r', linewidth=0.5)

        ax2 = fig.add_subplot(gs[0, 0], sharex=ax1)
        xyScale = np.meshgrid(xScale, yScale)
        im2 = ax2.pcolormesh(xyScale[0], xyScale[1], zImage)
        ax2.xaxis.set_visible(False)
        ax2.set_xlabel(xUnit)
        ax2.set_ylabel(yUnit)

        ax3 = fig.add_subplot(gs[1, 1], sharey=ax1)
        yzScale = np.meshgrid(yScale, zScale)
        im3 = ax3.pcolormesh(yzScale[0], yzScale[1], xImage)
        ax3.yaxis.set_visible(False)
        ax3.set_xlabel(yUnit)
        ax3.set_ylabel(zUnit)
        
        if zWidthPix>0:
            yCut = np.nansum(xImage[zCenPix-zWidthPix:zCenPix+zWidthPix, :], axis=0)
        else:
            yCut = xImage[zCenPix, :]
            
        ax0 = fig.add_subplot(gs[0, 1], sharex=ax3)
        ax0.yaxis.set_visible(False)
        ax4 = ax0.twinx()
        ax4.plot(yScale, yCut, 'k-')
        y1, y2 = ax4.get_ylim()
        ax4.plot(np.array([yScale[yCenPix],yScale[yCenPix]]), np.array([y1, y2]), color='g', linewidth=0.5)
        if yWidthPix>0:
            ax4.plot(np.array([yScale[yCenPix-yWidthPix],yScale[yCenPix-yWidthPix]]), 
                     np.array([y1, y2]), color='g', linewidth=0.5)
            ax4.plot(np.array([yScale[yCenPix+yWidthPix],yScale[yCenPix+yWidthPix]]), 
                     np.array([y1, y2]), color='g', linewidth=0.5)
        ax4.xaxis.set_visible(False)

        plt.tight_layout()
        
        cut = nData(yCut)
        cut.updateAx('x', yScale, yUnit)
    elif ax=='x':
        fig = plt.figure(figsize=(5,5))
        gs = fig.add_gridspec(2, 2)

        ax1 = fig.add_subplot(gs[1, 0])
        yzScale = np.meshgrid(yScale, zScale)
        im1 = ax1.pcolormesh(yzScale[0], yzScale[1], xImage)
        ax1.set_xlabel(yUnit)
        ax1.set_ylabel(zUnit)
        ax1.plot(yScale, np.ones(len(yScale))*zScale[zCenPix], color='r', linewidth=0.5)
        ax1.plot(np.ones(len(zScale))*yScale[yCenPix], zScale, color='b', linewidth=0.5)
        if yWidthPix>0:
            ax1.plot(np.ones(len(zScale))*yScale[yCenPix-yWidthPix], zScale, color='b', linewidth=0.5)
            ax1.plot(np.ones(len(zScale))*yScale[yCenPix+yWidthPix], zScale, color='b', linewidth=0.5)
        if zWidthPix>0:
            ax1.plot(yScale, np.ones(len(yScale))*zScale[zCenPix-zWidthPix], color='r', linewidth=0.5)
            ax1.plot(yScale, np.ones(len(yScale))*zScale[zCenPix+zWidthPix], color='r', linewidth=0.5)

        ax2 = fig.add_subplot(gs[0, 0], sharex=ax1)
        yxScale = np.meshgrid(yScale, xScale)
        im2 = ax2.pcolormesh(yxScale[0], yxScale[1], zImage.transpose())
        ax2.xaxis.set_visible(False)
        ax2.set_xlabel(yUnit)
        ax2.set_ylabel(xUnit)

        ax3 = fig.add_subplot(gs[1, 1], sharey=ax1)
        xzScale = np.meshgrid(xScale, zScale)
        im3 = ax3.pcolormesh(xzScale[0], xzScale[1], yImage)
        ax3.yaxis.set_visible(False)
        ax3.set_xlabel(xUnit)
        ax3.set_ylabel(zUnit)

        if yWidthPix>0:
            xCut = np.nansum(zImage[yCenPix-yWidthPix:yCenPix+yWidthPix,:], axis=0)
        else:
            xCut = zImage[yCenPix, :]
        
        ax0 = fig.add_subplot(gs[0, 1], sharex=ax3)
        ax0.yaxis.set_visible(False)
        ax4 = ax0.twinx()
        ax4.plot(xScale, xCut, 'k-')
        y1, y2 = ax4.get_ylim()
        ax4.plot(np.array([xScale[xCenPix],xScale[xCenPix]]), np.array([y1, y2]), color='g', linewidth=0.5)
        if xWidthPix>0:
            ax4.plot(np.array([xScale[xCenPix-xWidthPix],xScale[xCenPix-xWidthPix]]), 
                     np.array([y1, y2]), color='g', linewidth=0.5)
            ax4.plot(np.array([xScale[xCenPix+xWidthPix],xScale[xCenPix+xWidthPix]]), 
                     np.array([y1, y2]), color='g', linewidth=0.5)
        ax4.xaxis.set_visible(False)

        plt.tight_layout()
        
        cut = nData(xCut)
        cut.updateAx('x', xScale, xUnit)
        
    xImage = nData(xImage)
    xImage.updateAx('x', yScale, yUnit)
    xImage.updateAx('y', zScale, zUnit)
    
    yImage = nData(yImage)
    yImage.updateAx('x', xScale, xUnit)
    yImage.updateAx('y', zScale, zUnit)
    
    zImage = nData(zImage)
    zImage.updateAx('x', xScale, xUnit)
    zImage.updateAx('y', yScale, yUnit)
    
    return xImage, yImage, zImage, cut
