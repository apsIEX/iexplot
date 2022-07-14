#==============================================================================
# Scientific n-dim data analysis
# 2020-06-10
# Ver. 3
# Yue Cao (ycao@colorado.edu)
#
# 2020-10-20
# Ver. 4  jmcchesn@aps.anl.gov
# added Compare2D
#
#
#
#
# Main class: nData
# This class is for 1~3d numpy array stored together with the scales and units.
# This allows keeping the data together with the axes and units, just like in
# e.g. IgorPro.
#
# The intention is to manage most scientific data in e.g. ARPES, XRD.
#
# The main methods allow updating the scales, saving the data, etc.
# Thus we could keep the intermediate results and save them as h5.
# One could pick up where they left off without start-over.
#
# Our main class does have a drawback - it will use more memory whenever
# a new nData class instance is created. Setting the name of the instance to a
# nan or [] does not reduce the allocated memory due to the way python runs.
# Memory management is in general a headache in python. A workaround is 
# that we should update the unit and axis instead of creating a new class
# instance unless the actual data has been updated. Also, a good practice is
# to save the intermediate results more often and just load these results
# instead of re-running the ipynb. After all, disk space is cheap.
#
# Definition of axes - from inner most to outer most: x, y, z
#
# All the methods that do not generate a new class instance goes under the
# class definition. All others goes outside.
#
# Domain-specific codes e.g. ARPES goes as a new .py file using the nData
# instance as the inputs and outputs
#
#==============================================================================

# import all plotting packages
import matplotlib.pyplot as plt

# importing system packages
import os
import h5py

# importing the workhorse
import numpy as np


#==============================================================================
# Global variables in science
#==============================================================================

kB = 8.6173423e-05          # Boltzmann k in eV/K
me = 5.68562958e-32         # Electron mass in eV*(Angstroms^(-2))*s^2
hbar = 6.58211814e-16       # hbar in eV*s
hc_over_e = 12.4            # hc/e in keV⋅A


#==============================================================================
# Main class: nData
# For coding them, 'self' should be the first argument
# For using them, do not put in 'self'
#==============================================================================
class nData:
    """
    nData is an np.array or either 1,2,3 dimensions and shape=(z,y,x)
        2D: x/y-axis=1/0
        3D: x/y/z-axis=2/1/0 (i.e data[0,:,:]=image at first motor value)
    
    usage
        scan=nData(array)
        scan.data => array
        scan.scale => dictionary with scales (key:'x','y','z')
        scan.unit => dictionary with units (key:'x','y','z')
        
        scales: (scale_array can be a list or np.array)
            updateAx('x', scale_array, 'unit_string')
            updateScale('x', scale_array)
            shiftScale('x', old_x_value, new_x_value)
            updateUnit('x', 'unit_string')
        dataset info:
            scan.info() => prints shape and axis info
        extras:
            scan.extras() => dictionary with metadata -- see domain specific extensions
            for neccessary keys nData does not require
        scan.EDC = 1D nData object; sum over all angles
        scan.MDC = 1D nData object; sum over all energies
            
    """
    def __init__(self, data):
        self.data = data
        dim = len(data.shape)
        self.scale = {}
        self.unit = {}
        self.extras = {}
        self.scale['x'] = np.arange(data.shape[-1])
        self.unit['x'] = ''
        if dim>1:
            self.scale['y'] = np.arange(data.shape[-2])
            self.unit['y'] = ''
        if dim>2:
            self.scale['z'] = np.arange(data.shape[-3])
            self.unit['z'] = ''
        return


    def updateAx(self, ax, newScale, newUnit):
        '''
        Updating scales
        '''
        #print(len(self.scale[ax]))
        #print(len(newScale))
        if len(self.scale[ax])==len(newScale):
            self.scale[ax] = np.array(newScale)
            self.unit[ax] = newUnit
        else:
            print('Dimension {} mismatch!'.format(ax))
        return
    
    def updateScale(self, ax, newScale):
        if len(self.scale[ax])==len(newScale):
            self.scale[ax] = np.array(newScale)
        else:
            print('Dimension {} mismatch!'.format(ax))
        return
    
    def shiftScale(self, ax, oldCoor, newCoor):
        '''
        Shifting the scale along a given axis
        '''
        self.scale[ax] = self.scale[ax]-oldCoor+newCoor
        return
    
    def updateUnit(self, ax, newUnit):
        self.unit[ax] = newUnit
        return
    
    def updateExtras(self,extras):
        '''
        Updates metadata dictionary
        '''
        self.extras = extras
        return
    
    def updateExtrasByKey(self,key,val):
        '''
        replace by key
        '''
        extras=self.extras
        extras.update({key:val})
        return
        
    
    def info(self):
        '''
        Summarizing the current info
        '''
        dim = len(self.data.shape)
        print('The {}-dim data has shape {}'.format(dim, self.data.shape))
        print('Axis x: size - {}, unit - {}'.format(len(self.scale['x']), self.unit['x']))
        if dim>1:
            print('Axis y: size - {}, unit - {}'.format(len(self.scale['y']), self.unit['y']))
        if dim>2:
            print('Axis z: size - {}, unit - {}'.format(len(self.scale['z']), self.unit['z']))
        
        return

    
    def save(self, fname, fdir=''):
        if fdir=='':
            fdir = os.getcwd()
            
        fpath = os.path.join(fdir, fname+'.h5')
        
        if os.path.exists(fpath):
            print('Warning: Overwriting file {}.h5'.format(fname))
        h = h5py.File(fpath, 'w')
        
        h.create_dataset('data', data=self.data, dtype='f')
        
        scale = h.create_group('scale')
        for ax in self.scale.keys():
            scale.create_dataset(ax, data=self.scale[ax], dtype='f')
        
        unit = h.create_group('unit')
        for ax in self.unit.keys():
            unit.attrs[ax] = self.unit[ax]
        
        extras = h.create_group('extras')
        for key in self.extras.keys():
            extras.attrs[key] = self.extras[key]
        
        h.close()
        return


#==============================================================================
# Loading the nData class
#==============================================================================
def load_nData(fname, fdir=''):
    """
    Loads hdf5 files with the following format
         dataset:'data' dtype='f'
         
         group: 'scale'
            dataset:Xscale
            dataset:Zscale
        
        group: 'units'
            unit.attrs['x'] = 'Xunits'
            unit.attrs['y'] = 'Yunits'
            unit.attrs['z'] = 'Zunits'
            
        group: 'extras'
            extras.attrs[key] = value
    """
    if fdir=='':
        fdir = os.getcwd()
            
    fpath = os.path.join(fdir, fname+'.h5')
    h = h5py.File(fpath, 'r')
    
    data = np.array(h['data'])
    d = nData(data)
    
    for ax in h['scale'].keys():
        d.updateAx(ax, np.array(h['scale/'+ax]), h['unit'].attrs[ax])
    
    for key in h['extras'].keys():
        d.updateExtrasByKey(key,h['extras'].attrs[key])
    
    d.info()
    h.close()
    
    return d

##########################################
# generalized code for saving and loading as part of a large hd5f -JM 4/27/21
# creates/loads subgroups    
##########################################
def nData_h5Group_w(nd,parent,name):
    """
    for an nData object => nd
    creates an h5 group with name=name within the parent group:
        dataset => data
        group named: scale
            dataset => for each scale name ax
        group named: unit
            attrs[ax] => unit
        group named: extra
            attrs[key]                   
    """
    g=parent.create_group(name)
    g.create_dataset('data', data=nd.data, dtype='f')

    scale = g.create_group('scale')
    for ax in nd.scale.keys():
        scale.create_dataset(ax, data=nd.scale[ax], dtype='f')

    unit = g.create_group('unit')
    for ax in nd.unit.keys():
        unit.attrs[ax] = nd.unit[ax]

    extras = g.create_group('extras')
    for key in nd.extras.keys():
        extras.attrs[key] = nd.extras[key]   
    
    return g

def nData_h5Group_r(h):
    data=h['data'][:]
    d=nData(data)
    
    for ax in h['scale'].keys():
        d.updateAx(ax, np.array(h['scale/'+ax]), h['unit'].attrs[ax])
    
    for key in h['extras'].keys():
        d.updateExtrasByKey(key,h['extras'].attrs[key])
        
    return d

#==============================================================================
# Utils for appending/stacking
#==============================================================================


def nAppend(data1,data2,**kwargs):
	"""
	appends two 2D or 3D pynData data sets and returns nData volume (nVol)
	sets the scaling --- still need to work on
	nVol.extra['Append']=data1,data2
		kwargs:
			ax = 'x'|'y'|'z', axis to which to append, (default: ax='z')
			scale = 'data'|'point', sets the scaling base of the data or point number (default:data)
			extra = 1|2|None, copies the meta data from (data1),(data2),None (default:1)
	"""
	### defaults
	args={
		'ax':'z',
		'scale':'data'
	}
	args.update(kwargs) 
	
	if (len(np.shape(data1.data)) <2 ) or (len(np.shape(data2.data)) <2 ):
		print("Append only works for 2D or 3D datasets")
	else:
	## Making stack1 a volume
		if len(np.shape(data1.data)) <3:
			if args['ax']=='z':
				vol1=data1.data[np.newaxis,:,:]
			if args['ax'] =='y':
				vol1=data1.data[:,np.newaxis,:]
			if args['ax'] =='z':
				vol1=data1.data[:,:,np.newaxis]
		else:
			vol1=data1.data
	## Making stack2 a volume
		if len(np.shape(data2.data)) <3:
			if args['ax'] =='z':
				vol2=data2.data[np.newaxis,:,:]
			if args['ax'] =='y':
				vol2=data2.data[:,np.newaxis,:]
			if args['ax'] =='z':
				vol2=data2.data[:,:,np.newaxis]
		else:
			vol2=data2.data
	## Stacking vol2 ontop of vol1
		if args['ax'] =='x':
			if (np.shape(vol1)[1]==np.shape(vol2)[1]) and (np.shape(vol1)[2]==np.shape(vol2)[2]):
				vol1=np.dstack((vol1,vol2))
				xscale=np.append(data1.scale['x'],data2.scale['x'])
				yscale=data1.scale['y']
				zscale=data1.scale['z']
			else:
				print("Data sets must be the same size in y and z")
		if args['ax'] =='y':
			if (np.shape(vol1)[0]==np.shape(vol2)[0]) and (np.shape(vol1)[2]==np.shape(vol2)[2]):
				vol1=np.hstack((vol1,vol2))
				xscale=data1.scale['x']
				yscale=np.append(data1.scale['y'],data2.scale['y'])
				zscale=data1.scale['z']
			else:
				print("Data sets must be the same size in x and z")
		if args['ax'] =='z':
			if (np.shape(vol1)[0]==np.shape(vol2)[0]) and (np.shape(vol1)[1]==np.shape(vol2)[1]):
				vol1=np.vstack((vol1,vol2))
				xscale=data1.scale['x']
				yscale=data1.scale['y']
				zscale=np.append(data1.scale['z'],data2.scale['z'])
			else:
				print("Data sets must be the same size in x and y")
		nVol=nData(vol1)
		if args['scale']=='data': 
			nVol.updateAx('x',xscale,data1.unit['x'])
			nVol.updateAx('y',yscale,data1.unit['y'])
			nVol.updateAx('z',zscale,data1.unit['z'])
		nVol.extras.update({'nDataAppend',['data1','data2']})
		return nVol
	
#==============================================================================
# Utils for plotting and slicing
#==============================================================================

def niceplot(*ds,**plotkwargs):
    '''
    Simple plot for 1D and 2D nData
    *ds pndata files
    ** plotkwargs; matplotlib plot kwargs
        e.g.
        label="scan1"
    '''
    #plt.figure()
    d=ds[0]
    try:
        dim = len(d.data.shape)
        for d in list(ds):
            if dim==1:
                if(d.data.shape[0]<2):
                    print("Data is a single point "+str(d.data))
                else:
                    plt.plot(d.scale['x'], d.data,**plotkwargs)
                    plt.xlabel(d.unit['x'])
            elif dim==2:
                xx, yy = np.meshgrid(d.scale['x'], d.scale['y'])
                plt.pcolormesh(xx, yy, d.data)
                plt.xlabel(d.unit['x'])
                plt.ylabel(d.unit['y'])
            elif dim>2:
                print('Warning: niceplot can only plot 1d and 2d data.')
    except:
            print('Note a valid object')

    return


def niceplot_avg(d,ax='y',Cen=np.nan,WidthPix=np.nan):
    """
    bins 2D data in ax, with Center, and WidthPix 
    if Center=np.nan then center is the midpoint
    if WidthPix=np.nan then whole image is bined    
    """


    if(len(d.data.shape)==2):
        Scale=d.scale[ax]
        if np.isnan(Cen):
            CenPix = len(Scale)//2
        else:
            CenPix = np.argmin((Scale-Cen)**2)
        if np.isnan(WidthPix):
            WidthPix=len(Scale)//2

        if(ax=='x'):
            img_avg = np.nansum(d.data[:,CenPix-WidthPix:CenPix+WidthPix], axis=1)
            bx='y'
        elif(ax=='y'):
            img_avg = np.nansum(d.data[CenPix-WidthPix:CenPix+WidthPix,:], axis=0)
            bx='x'
        avg=nData(img_avg)
        avg.updateAx('x', d.scale[bx], d.unit[bx])
        niceplot(avg)
        
    else:
        print('only works for 2D data')


def plot2D(d, xCen=np.nan, xWidthPix=0, yCen=np.nan, yWidthPix=0, vmin=np.nan, vmax=np.nan):
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
	im1 = ax1.pcolormesh(xyScale[0], xyScale[1], img, vmin=vmin, vmax=vmax)
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
	if csr != None:
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
	if csr != None:
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
	if csr != None:
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
	if csr != None:
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
    if ax == 'z':
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
    elif ax == 'y':
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
    elif ax == 'x':
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
    if dim == 1:
        if ax == 'x':
            d_c = nData(d.data[idmin:idmax])
    elif dim == 2:
        if ax == 'y':
            d_c = nData(d.data[idmin:idmax])
        elif ax == 'x':
            d_c = nData(d.data[:, idmin:idmax])
    elif dim == 3:
        if ax == 'z':
            d_c = nData(d.data[idmin:idmax])
        elif ax == 'y':
            d_c = nData(d.data[:, idmin:idmax])
        elif ax == 'x':
            d_c = nData(d.data[:, :, idmin:idmax])
    else:
        print('Warning: cropping a non-existent dim.')
    
    for key in d.unit.keys():
        if key == ax:
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

    if not newhscale == []:
        newX = np.linspace(newhscale[0], newhscale[1], num=newhscale[2])

    if not newvscale == []:
        newY = np.linspace(newvscale[0], newvscale[1], num=newvscale[2])
    
    newXX, newYY = np.meshgrid(newX, newY)

    # Interpolate
    newImg = np.interpolate.griddata(points, values, (newXX, newYY), method='cubic')
    
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
    if ax == 'z':
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
    elif ax == 'y':
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
    elif ax == 'x':
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
    
    if type(nfold) == int and nfold>1:
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


#==============================================================================
# Wish lists:
# 1) mirror
# 2) 2nd dev

#==============================================================================




#==============================================================================
# Utils for 2nd dev along a given axis
#==============================================================================