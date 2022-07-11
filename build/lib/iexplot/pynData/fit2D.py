#==============================================================================
# 2D fitting
# 2020-05-20
# 
# Ver. 1
# Yue Cao (ycao@colorado.edu)
#
# General comments:
#
# 1) In all the inputs, the x and y are 1D, and the z is 2D.
#
# 2) We could put the actual scales of x and y (e.g. degrees, A^-1) as inputs.
# The outputs will be scaled accordingly.
#
# 3) The ROI is in pixels and not scaled, in the format of [xmin, xmax, ymin, ymax]
#
# For each fitting, there are 3 parts:
# The function for the model, the function making the initial guess
# and the minimization function. Note the misfit from the minimizer is 
# a flattened 2D array, and will have to be reshaped for comparison.
#
#==============================================================================

# import matplotlib as mpl
# mpl.rcParams['figure.dpi'] = 100

import matplotlib.pyplot as plt
from matplotlib import colors, cm
from mpl_toolkits.axes_grid1 import make_axes_locatable

# importing system packages
import os
import sys
import glob
import h5py
import time
import itertools

# importing the workhorse
import numpy as np
import pandas as pd
from scipy import io, signal, interpolate

# tiff packages
import tifffile

from lmfit import Minimizer, Parameters, report_fit

#==============================================================================
# Internal methods for converting values to indices
#==============================================================================

def _val_to_idx(x, val):
    '''
    Internal methods for converting values to indices
    
    x:              1D array, monotonic
    val:            A value
    '''
    idx = np.nanargmin((x-val)**2)
    
    return idx


def _lim_to_bounds(x, ROI):
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


#==============================================================================
# General fitting methods
#==============================================================================

def do_fit2D(x, y, z, model_func, guess_func, params=[], ROI=[], verbose=False, plotFit=False):
    '''
    General 2D fit func
    
    One could choose to put the initial guess by hand, or to use
    the automatic guess
    Inputs:
    x: 1D
    y: 1D
    z: 2D
    '''
    if not ROI==[]:
        xidmin, xidmax = _lim_to_bounds(x, [ROI[0], ROI[1]])
        yidmin, yidmax = _lim_to_bounds(y, [ROI[2], ROI[3]])
        tx = x[xidmin:xidmax]
        ty = y[yidmin:yidmax]
        tz = z[yidmin:yidmax, xidmin:xidmax]
    else:
        tx = x
        ty = y
        tz = z
    
    if params==[]:
        params = guess_func(tx, ty, tz)
        
    minner = Minimizer(model_func, params, fcn_args=(tx, ty, tz))
    result = minner.minimize()
    
    misfit = result.residual.reshape(tz.shape)*(-1)
    # fitted = tz + result.residual.reshape(tz.shape)
    fitted = tz-misfit
    chisqr = result.redchi
    
    # Getting all parameters
    fit_params = pd.DataFrame(index=params.keys(), columns=['value', 'err']).astype(float)
    for key in params.keys():
        fit_params['value'].loc[key] = result.params[key].value
        fit_params['err'].loc[key] = result.params[key].stderr

    if verbose:
        report_fit(result)
    
    if plotFit:
        fig, ax = plt.subplots(1,3)
        im0 = ax[0].imshow(tz)
        divider = make_axes_locatable(ax[0])
        cax = divider.append_axes("right", size="5%", pad=0.05)
        fig.colorbar(im0, cax=cax)
        ax[0].set_title('Raw data')
        
        im1 = ax[1].imshow(fitted)
        divider = make_axes_locatable(ax[1])
        cax = divider.append_axes("right", size="5%", pad=0.05)
        fig.colorbar(im1, cax=cax)
        ax[1].set_title('Fit')
        im2 = ax[2].imshow(misfit)
        divider = make_axes_locatable(ax[2])
        cax = divider.append_axes("right", size="5%", pad=0.05)
        fig.colorbar(im2, cax=cax)
        ax[2].set_title('Misfit')
        fig.tight_layout()
        
        fig, ax = plt.subplots(1,2)
        ax[0].plot(tz.sum(axis=1), 'b.', label='Raw')
        ax[0].plot(fitted.sum(axis=1), 'r-', label='Fit')
        ax[0].plot(misfit.sum(axis=1), 'k--', label='Misfit')
        ax[0].legend()
        ax[0].set_xlabel('x')
        ax[0].set_title('Summed along y')
        ax[1].plot(tz.sum(axis=0), 'b.', label='Raw')
        ax[1].plot(fitted.sum(axis=0), 'r-', label='Fit')
        ax[1].plot(misfit.sum(axis=0), 'k--', label='Misfit')
        ax[1].legend()
        ax[1].set_xlabel('y')
        ax[1].set_title('Summed along x')
        fig.tight_layout()
    
    return fit_params, tx, ty, tz, fitted, misfit, chisqr


def fitted_to_params2D(fit_params):
    '''
    Transferring fitted
    values into the guess of another fit
    
    The bounds and constraints will not be transferred
    '''
    params = Parameters()
    for key in fit_params.index:
        params.add(key, value=fit_params['value'].loc[key])
        
    return params


#==============================================================================
# Anisotropic Gaussian
#==============================================================================
def Gauss2D(params, x, y, z):
    '''
    2D Gaussian
    https://en.wikipedia.org/wiki/Gaussian_function#Two-dimensional_Gaussian_function
    
    Input:
    x: x coordinate, 1D
    y: y coordinate, 1D
    z: height values
    '''
    A = params['Area']
    sx = params['sigma_x']
    sy = params['sigma_y']
    xc = params['cen_x']
    yc = params['cen_y']
    
    bg_x = params['BG_slope_x']
    bg_y = params['BG_slope_y']
    bg_c = params['BG_const']
    
    xx, yy = np.meshgrid(x, y)
    
    model = A*np.exp(-(xx-xc)**2/2/sx**2-(yy-yc)**2/2/sy**2)/(2*np.pi*sx*sy)
    model = model+bg_x*xx+bg_y*yy+bg_c
    
    return model-z


def guess_Gauss2D(x, y, z):
    '''
    Making initial guess
    x, y can be identified as pixel number, or if in need, HKL values
    '''
    xx, yy = np.meshgrid(x, y)
    
    # Guessing the center
    cen = np.unravel_index(z.argmax(), z.shape)
    yc = y[cen[0]]
    xc = x[cen[1]]
    
    # Guessing the BG
    bg_c = np.nanmin(z)
    height = np.nanmax(z)-bg_c
    
    # Guessing the widths and BG slopes
    temp = z[cen[0]]
    bg_x = (temp[-1]-temp[0])/(x[-1]-x[0])
    templeft = temp[:cen[1]]
    sx_left = np.argwhere(templeft<bg_c+height/2)[-1,0]
    tempright = temp[cen[1]:]
    sx_right = np.argwhere(tempright<bg_c+height/2)[0,0]
    sx = np.abs((x[sx_right]-x[sx_left])/2.)
    
    temp = z[:, cen[1]]
    bg_y = (temp[-1]-temp[0])/(y[-1]-y[0])
    templeft = temp[:cen[0]]
    sy_left = np.argwhere(templeft<bg_c+height/2)[-1,0]
    tempright = temp[cen[0]:]
    sy_right = np.argwhere(tempright<bg_c+height/2)[0,0]
    sy = np.abs((y[sy_right]-y[sy_left])/2.)
    
    # Guessing the area
    A = 2*np.pi*sx*sy*height
    
    params = Parameters()
    params.add('Area', value=A)
    params.add('sigma_x', value=sx)
    params.add('sigma_y', value=sy)
    params.add('cen_x', value=xc)
    params.add('cen_y', value=yc)
    params.add('BG_slope_x', value=bg_x)
    params.add('BG_slope_y', value=bg_y)
    params.add('BG_const', value=bg_c)
    
    return params


#==============================================================================
# Anisotropic Lorentzian
#==============================================================================
def Lor2D(params, x, y, z):
    '''
    Note Lor2D has a height but not an area.
    The -inf to inf integral does not converge.
    '''
    H = params['Height']
    fwhm_x = params['FWHM_x']
    fwhm_y = params['FWHM_y']
    xc = params['cen_x']
    yc = params['cen_y']
    
    bg_x = params['BG_slope_x']
    bg_y = params['BG_slope_y']
    bg_c = params['BG_const']
    
    xx, yy = np.meshgrid(x, y)
    
    model = H/(((xx-xc)*2/fwhm_x)**2+((yy-yc)*2/fwhm_y)**2+1)
    model = model+bg_x*xx+bg_y*yy+bg_c
    
    return model-z


def guess_Lor2D(x, y, z):
    '''
    Making initial guess
    x, y can be identified as pixel number, or if in need, HKL values
    '''
    xx, yy = np.meshgrid(x, y)
    
    # Guessing the center
    cen = np.unravel_index(z.argmax(), z.shape)
    yc = y[cen[0]]
    xc = x[cen[1]]
    
    # Guessing the BG
    bg_c = np.nanmin(z)
    height = np.nanmax(z)-bg_c
    
    # Guessing the widths and BG slopes
    temp = z[cen[0]]
    bg_x = (temp[-1]-temp[0])/(x[-1]-x[0])
    templeft = temp[:cen[1]]
    sx_left = np.argwhere(templeft<bg_c+height/2)[-1,0]
    tempright = temp[cen[1]:]
    sx_right = np.argwhere(tempright<bg_c+height/2)[0,0]
    fwhm_x = np.abs(x[sx_right]-x[sx_left])
    
    temp = z[:, cen[1]]
    bg_y = (temp[-1]-temp[0])/(y[-1]-y[0])
    templeft = temp[:cen[0]]
    sy_left = np.argwhere(templeft<bg_c+height/2)[-1,0]
    tempright = temp[cen[0]:]
    sy_right = np.argwhere(tempright<bg_c+height/2)[0,0]
    fwhm_y = np.abs(y[sy_right]-y[sy_left])
    
    params = Parameters()
    params.add('Height', value=height)
    params.add('FWHM_x', value=fwhm_x)
    params.add('FWHM_y', value=fwhm_y)
    params.add('cen_x', value=xc)
    params.add('cen_y', value=yc)
    params.add('BG_slope_x', value=bg_x)
    params.add('BG_slope_y', value=bg_y)
    params.add('BG_const', value=bg_c)
    
    return params

