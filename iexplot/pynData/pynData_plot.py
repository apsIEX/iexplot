import numpy as np
import matplotlib.pyplot as plt 

from iexplot.pynData.pynData import nData
from iexplot.plotting import plot_1D,plot_2D,plot_3D
#==============================================================================
# Utils for plotting and slicing
#==============================================================================

def niceplot(*ds,**kwargs):
    '''
    Simple plot for 1D and 2D nData
    *ds pnData files
	**kwargs see plot_2D and plot_3D
	**kwargs plot_1D
        xrange=[x_first,x_last] to plot subrange 
        Norm2One: True/False to normalize graph between zero and one
        offset: y -= offset 
        offset_mean_index: y -= np.mean(y[scale_mean_index[0]:scale_mean_index[-1]])
        scale: y *= scale
        scale_mean_index: y /= np.mean(y[scale_mean_index[0]:scale_mean_index[-1]])
        offset_x: x += offset_x 
        scale_x: x *= scale_x


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
                plot_2D(img,scales,units,**kwargs)
                
            elif dim==3:
                img = d.data
                scales = [d.scale['y'],d.scale['x'],d.scale['z']]
                units = [d.unit['y'],d.unit['x'],d.unit['z']]
                plot_3D(img,scales,units,**kwargs)
				
            else:
                print('Warning: niceplot can only plot 1d and 2d data.')
    except:
            print('Not a valid object')
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
