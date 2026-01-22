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
#from matplotlib import colors, cm
#from mpl_toolkits.axes_grid1 import make_axes_locatable

# importing system packages
import os
#import sys
#import glob
import h5py
#import time
#import itertools

# importing the workhorse
import numpy as np
#import pandas as pd
#from scipy import io, signal, interpolate, ndimage
#from math import floor

from iexplot.utilities import take_closest_value
from iexplot.plotting import find_closest


#==============================================================================
# Main class: nData
# For coding them, 'self' should be the first argument
# For using them, do not put in 'self'
#==============================================================================
class nData:
    """
    nData is an np.array or either 1,2,3 dimensions and shape=(z,y,x)
        2D: shape = (y,x)
        3D: shape = (y,x,z) (i.e data[0,:,:]=image at first motor value)
        

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
            
    """
    def __init__(self, data):
        """
        modify to pass (recast)
        """
        if isinstance(data,nData):
            pass
        else:
            self.data = data
            dim = len(data.shape)
            self.scale = {}
            self.unit = {}
            self.extras = {}
            if dim == 1:
                self.scale['x'] = np.arange(data.shape[0])
                self.unit['x'] = ''
            else:
                self.scale['x'] = np.arange(data.shape[1])
                self.unit['x'] = ''
                self.scale['y'] = np.arange(data.shape[0])
                self.unit['y'] = ''
                if dim > 2:
                    self.scale['z'] = np.arange(data.shape[2])
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
        
        scale = h.create_grsaveoup('scale')
        for ax in self.scale.keys():
            scale.create_dataset(ax, data=self.scale[ax], dtype='f')
        
        unit = h.create_group('unit')
        for ax in self.unit.keys():
            unit.attrs[ax] = self.unit[ax]
        
        extras = h.create_group('extras')
        if len(self.extras[0]) != 0:
            for key in self.extras.keys():
                extras.attrs[key] = self.extras[key]
        '''

        for group in self.keys():
            group = h.create_group('group')
            if group == 'scale':
                for ax in self.group.keys():
                    group.create_dataset(ax, data=self.scale[ax], dtype='f')
            elif group == 'unit':
                for ax in self.group.keys():
                    group.attrs[ax] = self.unit[ax]
            else:
                for key in self.group.keys():
                    group.attrs[key] = self.group[key]

        for group in self.keys():
            
        '''



        h.close()
        return
    
    def crop_x(self, crop_start, crop_end, **kwargs):
        """
        crops nData object in the x dimension
        works for dim = 1,2,3
        crop_start/end = index (default) or coordinate range to crop

        kwargs 
            index = False (default) to crop by coordinate
                  = True to crop by index
        """
        kwargs.setdefault('index', False)

        if kwargs['coord']:
            px_min = crop_start
            px_max = crop_end
        else:
            coord_min = take_closest_value(self.scale['x'], crop_start)
            index_min = np.where(self.scale['x'] == coord_min)[0][0]
            
            coord_max = take_closest_value(self.scale['x'], crop_end)
            index_max = np.where(self.scale['x'] == coord_max)[0][0]

            #if x-axis is flipped (i.e. for BE), need to flip bounds as well
            px_min = min(index_min,index_max)
            px_max = max(index_min,index_max)


        dims = len(self.data.shape)
        if dims == 3:
            self.data = self.data[:,px_min:px_max,:]
            self.scale['x'] = self.scale['x'][px_min:px_max]
        elif dims == 2:            
            self.data = self.data[:,px_min:px_max]
            self.scale['x'] = self.scale['x'][px_min:px_max]
        elif dims == 1:
            self.data = self.data[px_min:px_max]
            self.scale['x'] = self.scale['x'][px_min:px_max]
        else:
            print("Data needs to have 1, 2, or 3 dimensions, not ",str(dims))
        

    def crop_y(self,crop_start, crop_end, **kwargs):
        """
        crops nData object in the x dimension
        works for dim = 1,2,3
        """

        kwargs.setdefault('coord', False)

        if kwargs['index']:
            px_min = crop_start
            px_max = crop_end
        else:
            coord_min = take_closest_value(self.scale['y'], crop_start)
            index_min = np.where(self.scale['y'] == coord_min)[0][0]
            
            coord_max = take_closest_value(self.scale['y'], crop_end)
            index_max = np.where(self.scale['y'] == coord_max)[0][0]

            #if x-axis is flipped (i.e. for BE), need to flip bounds as well
            px_min = min(index_min,index_max)
            px_max = max(index_min,index_max)


        dims = len(self.data.shape)

        if dims == 3:
            self.data = self.data[px_min:px_max,:,:]
            self.scale['y'] = self.scale['y'][px_min:px_max]
        elif dims == 2:
            self.data = self.data[px_min:px_max,:]
            self.scale['y'] = self.scale['y'][px_min:px_max]
        else:
            print("Data needs to have 2 or 3 dimensions, not ",str(dims))

    def crop_z(self,crop_start, crop_end, **kwargs):
        """
        crops nData object in the x dimension
        works for dim = 1,2,3
        """
        kwargs.setdefault('coord', False)

        if kwargs['index']:
            px_min = crop_start
            px_max = crop_end
        else:
            coord_min = take_closest_value(self.scale['z'], crop_start)
            index_min = np.where(self.scale['z'] == coord_min)[0][0]
            
            coord_max = take_closest_value(self.scale['z'], crop_end)
            index_max = np.where(self.scale['z'] == coord_max)[0][0]

            #if x-axis is flipped (i.e. for BE), need to flip bounds as well
            px_min = min(index_min,index_max)
            px_max = max(index_min,index_max)


        dims = len(self.data.shape)

        if dims == 3:
            self.data = self.data[:,:,px_min:px_max]
            self.scale['z'] = self.scale['z'][px_min:px_max]
        else:
            print("Data needs to have 3 dimensions, not ",str(dims))


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
    g=parent.require_group(name)
    g.require_dataset('data', data=nd.data, dtype='f',shape=nd.data.shape)

    scale = g.require_group('scale')
    for ax in nd.scale.keys():
        scale.require_dataset(ax, data=nd.scale[ax], dtype='f', shape=nd.scale[ax].shape)

    unit = g.require_group('unit')
    for ax in nd.unit.keys():
        unit.attrs[ax] = nd.unit[ax]

    extras = g.require_group('extras')
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
# Utils for appending/dstacking
#==============================================================================

def ndstack(nData_list,dstack_scale=None,dstack_unit="", **kwargs):
    """
    returns a dstack of nData objects 
    nData_list = list of nData objects, where the first element is the base object 
    dstack_scale = np.array for scaling (does not need to be monotonic)
                = None => index
   
    **kwargs
        extras: standard nData extras dictionary
    """
    kwargs.setdefault('debug',False)
    kwargs.setdefault('extras',{})

    if type(dstack_scale) == None:
        dstack_scale = np.arange(1,len(nData_list)+1)

    #dstacking the data
    dstacklist = []
    
    

    for i,d in enumerate(nData_list):
        if kwargs['debug']:
            print(d.data.shape)
        rank = len(d.data.shape)
        if i==0:
            dstacklist = []
            if kwargs['debug'] == True:
                print('rank = '+str(rank))
            dstack = d.data
            xscale = d.scale['x']
            xunit = d.unit['x']
            if rank == 1:
                yscale = np.array(dstack_scale[i])
                yunit = dstack_unit
            elif rank == 2:
                yscale = d.scale['y']
                yunit = d.unit['y']
                if len(nData_list[i+1].data.shape) == 1: #adding 1D to image
                    zscale = None
                    zunit = ''
                elif len(nData_list[i+1].data.shape) == 2: #adding 2D to image
                    zscale = np.array(dstack_scale[i])
                    zunit = dstack_unit   
                elif len(nData_list[i+1].data.shape) == 3: #adding 2D to 3D
                    zscale = d.scale['z']
                    zunit = d.unit['z']
            else:
                print('Can only dstack 1D, 2D and 3D data sets')
        else:
            if rank == 1: #dstacking along y
                dstack=np.vdstack((dstack,d.data))
                yscale=dstack_scale
                yunit = dstack_unit

            else: #dstacking along z
                dstack=np.dstack((dstack,d.data))
                zscale=dstack_scale
                zunit = dstack_unit
    

    d = nData(dstack)
    if rank == 1:
        if kwargs['debug'] == True:
            print('updating scales rank 1')
        d.updateAx('x', xscale, xunit)
        d.updateAx('y', yscale, yunit)
        
    else:
        if kwargs['debug'] == True:
            print('updating scales rank > 1')
            print(xunit,yunit,zunit)
        d.updateAx('z', zscale, zunit)
        d.updateAx('y', yscale, yunit)
        d.updateAx('x', xscale, xunit)
    #metadata_dstack(nData_list,d) temporarily commented out to troubleshoot AJE

    return d

    
def nAppend(data1,data2,**kwargs):
    """
    appends  pynData data sets along ax axis
        2D(x,y)
        3D(x,y,z)


    sets the scaling --- still need to work on
    nVol.extra['Append']=data1,data2
        kwargs:
            ax = 'x'|'y'|'z', axis to which to append, (default: ax='z')
            scale = 'data'|'point', sets the scaling base of the data or point number (default:data)
            extra = 1|2|None, copies the meta data from (data1),(data2),None (default:1)
    """
    kwargs.setdefault('ax','z')
    kwargs.setdefault('scale','data')

    if (len(np.shape(data1.data)) <2 ) or (len(np.shape(data2.data)) <2 ):
        print("Append only works for 2D or 3D datasets")
    else:
    ## Making dstack1 a volume
        if len(np.shape(data1.data)) <3:
            if kwargs['ax'] == 'x':
                vol1=data1.data[np.newaxis,:,:]
            if kwargs['ax']  == 'y':
                vol1=data1.data[:,np.newaxis,:]
            if kwargs['ax']  == 'z':
                vol1=data1.data[:,:,np.newaxis]
        else:
            vol1=data1.data
    ## Making dstack2 a volume
        if len(np.shape(data2.data)) <3:
            if kwargs['ax']  == 'x':
                vol2=data2.data[np.newaxis,:,:]
            if kwargs['ax']  == 'y':
                vol2=data2.data[:,np.newaxis,:]
            if kwargs['ax']  == 'z':
                vol2=data2.data[:,:,np.newaxis]
        else:
            vol2=data2.data
    ## dStacking vol2 ontop of vol1
        if kwargs['ax']  == 'x':
            if (np.shape(vol1)[1]==np.shape(vol2)[1]) and (np.shape(vol1)[2]==np.shape(vol2)[2]):
                vol1=np.ddstack((vol1,vol2))
                xscale=np.append(data1.scale['x'],data2.scale['x'])
                yscale=data1.scale['y']
                zscale=data1.scale['z']
            else:
                print("Data sets must be the same size in y and z")
        if kwargs['ax']  == 'y':
            if (np.shape(vol1)[0]==np.shape(vol2)[0]) and (np.shape(vol1)[2]==np.shape(vol2)[2]):
                vol1=np.hdstack((vol1,vol2))
                xscale=data1.scale['x']
                yscale=np.append(data1.scale['y'],data2.scale['y'])
                zscale=data1.scale['z']
            else:
                print("Data sets must be the same size in x and z")
        if kwargs['ax']  == 'z':
            if (np.shape(vol1)[0]==np.shape(vol2)[0]) and (np.shape(vol1)[1]==np.shape(vol2)[1]):
                vol1=np.vdstack((vol1,vol2))
                xscale=data1.scale['x']
                yscale=data1.scale['y']
                zscale=np.append(data1.scale['z'],data2.scale['z'])
            else:
                print("Data sets must be the same size in x and y")
        nVol=nData(vol1)
        if kwargs['scale'] == 'data': 
            nVol.updateAx('x',xscale,data1.unit['x'])
            nVol.updateAx('y',yscale,data1.unit['y'])
            nVol.updateAx('z',zscale,data1.unit['z'])
        nVol.extras.update({'nDataAppend',['data1','data2']})
        return nVol
	

def metadata_dstack(nData_list,ddstack):
    """
    dStacking metadata
    """
    for i,d in enumerate(nData_list): #iterates over each EA in mda
        keys_i = list(vars(nData_list[i]).keys()) 
        for key in keys_i: #iterates over each key in EA
            if key not in ['data','scale','unit']:
                val_i = getattr(d,key)
                if i == 0:
                    setattr(ddstack,key,[val_i]) #sets first key as attribute
                else:
                    if type(val_i) == np.ndarray: #arrays get dstacked in dimension 2
                        val = getattr(ddstack,key)
                        val = np.vdstack((val_i, val))
                    elif type(val_i) == str: #strings are put into a list
                        val = getattr(ddstack,key)
                        val.append(val_i)
                    else: #everything else gets put into np arrays
                        val = np.array(getattr(ddstack,key))
                        np.append(val,[val_i])
                    #val = np.array(val)
                    setattr(ddstack,key,val)



def slice_dstack(axes,dstack,c,b):
    """
    returns a slice from a 3D dstack
    
    axes = 'xy','yx','xz','zx','yz','zy' of desired slice
    dstack = 3D nData object with monotonic scaling
    c = [x,y,z] where to slice in scale space
    b = [bin_x,bin_y,bin_z], how much to bin

    """
    #convert cursor from scale to pixel
    c_px = []
    for i,ax in enumerate(dstack.scale.keys()):
        c_px.append(int(find_closest(dstack.scale[ax],c[i])[0]))
    
    #convert bin from scale to pixel
    b_px = []
    for i,ax in enumerate(dstack.scale.keys()):
        b_px.append(int(b[i]/(dstack.scale[ax][1]-dstack.scale[ax][0])))
    #note that dstack.data is  [y,x,z], while 
    ar = dstack.data.transpose((1, 0, 2))

    #slicing the dstack 
    if axes == 'yz':
        img = np.nansum(ar[c_px[0]-b_px[0]:c_px[0]+max(b_px[0],1),:,:],axis=0)
        img = nData(img.T)
        img.updateAx('x', dstack.scale['y'], dstack.unit['y'])
        img.updateAx('y', dstack.scale['z'], dstack.unit['z'])
    
    elif axes == 'zy':
        img = np.nansum(ar[c_px[0]-b_px[0]:c_px[0]+max(b_px[0],1),:,:],axis=0)
        img = nData(img)
        img.updateAx('y', dstack.scale['y'], dstack.unit['y'])
        img.updateAx('x', dstack.scale['z'], dstack.unit['z'])
    
    elif axes == 'xz':
        img = np.nansum(ar[:,c_px[1]-b_px[1]:c_px[1]+max(b_px[1],1),:],axis=1)
        img = nData(img.T)
        img.updateAx('x', dstack.scale['x'], dstack.unit['x'])
        img.updateAx('y', dstack.scale['z'], dstack.unit['z'])

    elif axes == 'zx':
        img = np.nansum(ar[:,c_px[1]-b_px[1]:c_px[1]+max(b_px[1],1),:],axis=1)
        img = nData(img)
        img.updateAx('y', dstack.scale['x'], dstack.unit['x'])
        img.updateAx('x', dstack.scale['z'], dstack.unit['z'])        
    
    elif axes == 'xy':
        img = np.nansum(ar[:,:,c_px[2]-b_px[2]:c_px[2]+max(b_px[2],1)],axis=2)
        img = nData(img.T)
        img.updateAx('x', dstack.scale['x'], dstack.unit['x'])
        img.updateAx('y', dstack.scale['y'], dstack.unit['y'])

    elif axes == 'yx':
        img = np.nansum(ar[:,:,c_px[2]-b_px[2]:c_px[2]+max(b_px[2],1)],axis=2)
        img = nData(img)
        img.updateAx('y', dstack.scale['x'], dstack.unit['x'])
        img.updateAx('x', dstack.scale['y'], dstack.unit['y']) 

    extras = dstack.extras
    extras.update({'slice_cb':(c,b)})
    img.updateExtras(extras)
    return img    



#==============================================================================
# Wish lists:
# 1) mirror
# 2) 2nd dev

#==============================================================================




#==============================================================================
# Utils for 2nd dev along a given axis
#==============================================================================