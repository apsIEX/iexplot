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
        '''
        scale = h.create_group('scale')
        for ax in self.scale.keys():
            scale.create_dataset(ax, data=self.scale[ax], dtype='f')
        
        unit = h.create_group('unit')
        for ax in self.unit.keys():
            unit.attrs[ax] = self.unit[ax]
        
        extras = h.create_group('extras')
        for key in self.extras.keys():
            extras.attrs[key] = self.extras[key]
        '''

        for group in self:
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
# Utils for appending/stacking
#==============================================================================
def nstack(nData_list,stack_scale=None,stack_unit="", **kwargs):
    """
    returns a stack of nData objects 
    nData_list = list of nData objects, where the first element is the base object 
    stack_scale = np.array for scaling (does not need to be monotonic)
                = None => index
   
    **kwargs
        extras: standard nData extras dictionary
    """
    kwargs.setdefault('debug',False)
    kwargs.setdefault('extras',{})

    if type(stack_scale) == None:
        stack_scale = np.arange(1,len(nData_list)+1)

    #stacking the data
    stacklist = []
    
    for i,d in enumerate(nData_list):
        rank = len(d.data.shape)
        if i==0:
            stacklist = []
            if kwargs['debug'] == True:
                print('rank = '+str(rank))
            stack = d.data
            xscale = d.scale['x']
            xunit = d.unit['x']
            if rank == 1:
                yscale = np.array(stack_scale[i])
                yunit = stack_unit
            elif rank == 2:
                yscale = d.scale['y']
                yunit = d.unit['y']
                if len(nData_list[i+1].data.shape) == 1: #adding 1D to image
                    zscale = None
                    zunit = ''
                elif len(nData_list[i+1].data.shape) == 2: #adding 2D to image
                    zscale = np.array(stack_scale[i])
                    zunit = stack_unit   
                elif len(nData_list[i+1].data.shape) == 3: #adding 2D to 3D
                    zscale = d.scale['z']
                    zunit = d.unit['z']
            else:
                print('Can only stack 1D, 2D and 3D data sets')
        else:
            if rank == 1: #stacking along y
                stack=np.vstack((stack,d.data))
                yscale=stack_scale
                yunit = stack_unit

            else: #stacking along z
                stack=np.dstack((stack,d.data))
                zscale=stack_scale
                zunit = stack_unit
    

    d = nData(stack)
    if rank == 1:
        if kwargs['debug'] == True:
            print('updating scales rank 1')
        d.updateAx('x', xscale, xunit)
        d.updateAx('y', yscale, yunit)
        print(yscale)
    else:
        if kwargs['debug'] == True:
            print('updating scales rank > 1')
            print(xunit,yunit,zunit)
        d.updateAx('z', zscale, zunit)
        d.updateAx('y', yscale, yunit)
        d.updateAx('x', xscale, xunit)
    metadata_stack(nData_list,d)

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
    ## Making stack1 a volume
        if len(np.shape(data1.data)) <3:
            if kwargs['ax'] == 'z':
                vol1=data1.data[np.newaxis,:,:]
            if kwargs['ax']  == 'y':
                vol1=data1.data[:,np.newaxis,:]
            if kwargs['ax']  == 'z':
                vol1=data1.data[:,:,np.newaxis]
        else:
            vol1=data1.data
    ## Making stack2 a volume
        if len(np.shape(data2.data)) <3:
            if kwargs['ax']  == 'z':
                vol2=data2.data[np.newaxis,:,:]
            if kwargs['ax']  == 'y':
                vol2=data2.data[:,np.newaxis,:]
            if kwargs['ax']  == 'z':
                vol2=data2.data[:,:,np.newaxis]
        else:
            vol2=data2.data
    ## Stacking vol2 ontop of vol1
        if kwargs['ax']  == 'x':
            if (np.shape(vol1)[1]==np.shape(vol2)[1]) and (np.shape(vol1)[2]==np.shape(vol2)[2]):
                vol1=np.dstack((vol1,vol2))
                xscale=np.append(data1.scale['x'],data2.scale['x'])
                yscale=data1.scale['y']
                zscale=data1.scale['z']
            else:
                print("Data sets must be the same size in y and z")
        if kwargs['ax']  == 'y':
            if (np.shape(vol1)[0]==np.shape(vol2)[0]) and (np.shape(vol1)[2]==np.shape(vol2)[2]):
                vol1=np.hstack((vol1,vol2))
                xscale=data1.scale['x']
                yscale=np.append(data1.scale['y'],data2.scale['y'])
                zscale=data1.scale['z']
            else:
                print("Data sets must be the same size in x and z")
        if kwargs['ax']  == 'z':
            if (np.shape(vol1)[0]==np.shape(vol2)[0]) and (np.shape(vol1)[1]==np.shape(vol2)[1]):
                vol1=np.vstack((vol1,vol2))
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
	

def metadata_stack(nData_list,dstack):
    """
    Stacking metadata
    """
    for i,d in enumerate(nData_list):
        keys_i = list(vars(nData_list[i]).keys())
        for key in keys_i:
            if key not in ['data','scale','unit']:
                val_i = getattr(d,key)
                if i == 0:
                    setattr(dstack,key,[val_i])
                else:
                    val = getattr(dstack,key)
                    val.append(val_i)
                    setattr(dstack,key,val)






#==============================================================================
# Wish lists:
# 1) mirror
# 2) 2nd dev

#==============================================================================




#==============================================================================
# Utils for 2nd dev along a given axis
#==============================================================================