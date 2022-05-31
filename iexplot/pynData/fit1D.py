#==============================================================================
# 1D fitting
# 2020-06-05
# 
# Ver. 3
# Yue Cao (ycao@colorado.edu)
#
# For each fitting, there are 2 parts:
# The function for the model and the function making the initial guess
# 
# For the actual fit, it is possible to put
# the initial guess by hand, or use the function to make a guess
#
#==============================================================================

# import all plotting packages
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
from scipy import io, signal, interpolate, ndimage

# tiff packages
import tifffile

from lmfit import Minimizer, Parameters, report_fit


#==============================================================================
# Global variables and physical consts
#==============================================================================

kB = 8.6173423e-05          # Boltzmann k in eV/K
me = 5.68562958e-32         # Electron mass in eV*(Angstroms^(-2))*s^2
hbar = 6.58211814e-16       # hbar in eV*s
hc_over_e = 12.4            # hc/e in keV⋅A


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
def do_fit(x, y, model_func, guess_func, params=[], ROI=[], verbose=False, plotFit=False):
    '''
    General fit func
    
    One could choose to put the initial guess by hand, or to use
    the automatic guess
    '''
    if not ROI==[]:
        idmin, idmax = _lim_to_bounds(x, ROI)
        tx = x[idmin:idmax]
        ty = y[idmin:idmax]
    else:
        tx = x
        ty = y
    
    if params==[]:
        params = guess_func(tx, ty)

    # Old ver - it is possible to have a model with kwargs
    # We removed the kwargs to reduce redundancy
    # minner = Minimizer(model_func, param, fcn_args=(x, y), fcn_kws={'ROI':ROI})
    
    minner = Minimizer(model_func, params, fcn_args=(tx, ty))
    result = minner.minimize()
    
    misfit = result.residual*(-1)
    # fitted = ty + result.residual
    fitted = ty-misfit
    chisqr = result.redchi
    
    # Getting all parameters
    fit_params = pd.DataFrame(index=params.keys(), columns=['value', 'err']).astype(float)
    for key in params.keys():
        fit_params['value'].loc[key] = result.params[key].value
        fit_params['err'].loc[key] = result.params[key].stderr

    if verbose:
        report_fit(result)
        
    if plotFit:
        plt.figure()
        plt.plot(tx, ty, 'b.')
        plt.plot(tx, fitted, 'r-')
        plt.plot(tx, misfit, 'k--')
    
    return fit_params, tx, ty, fitted, misfit, chisqr


def fitted_to_params(fit_params):
    '''
    Transferring fitted
    values into the guess of another fit
    
    The bounds and constraints will not be transferred
    '''
    params = Parameters()
    for key in fit_params.index:
        params.add(key, value=fit_params['value'].loc[key])
        
    return params


def batch_fit(x, y, img, fit_ax, model_func, guess_func, params=[], ROI=[], mode='sequential', plotFit=False):
    '''
    Batch fit to Fermi func with linear BG
    
    x:              1D array, x axis (does not need to be linear)
    y:              1D array, y axis (does not need to be linear)
    img:            2D array
    fit_ax:         Along which axis the fit will be done
    ROI:            A list in the format [xmin, xmax, ymin, ymax]
    mode:           There are two modes:
                    1) 'sequential' - the results from the 1st fit goes to the 2nd, etc.
                    2) 'independent' - each param is ...
    '''
    if not ROI==[]:
        xidmin, xidmax = _lim_to_bounds(x, ROI[:2])
        yidmin, yidmax = _lim_to_bounds(y, ROI[2:])
        
        tx = x[xidmin:xidmax]
        ty = y[yidmin:yidmax]
        timg = img[yidmin:yidmax, xidmin:xidmax]
        
        print(timg.shape)
    else:
        tx = x
        ty = y
        timg = img
    
    if fit_ax=='x': # Fit along horizontal
        fit_params, _, _, _, _, chisqr = do_fit(tx, timg[0], model_func, guess_func, 
                                                params=params, verbose=False, plotFit=False)
        fit_vals = fit_params['value']
        fit_errs = fit_params['err']
        fit_chisqrs = [chisqr]
        for i in range(1, timg.shape[0]):
            if mode=='sequential':
                newguess = fitted_to_params(fit_params)
            else:
                # Doing minner.minimize() will not change the input params
                newguess = params
            fit_params, _, _, _, _, chisqr = do_fit(tx, timg[i], model_func, guess_func, 
                                                params=newguess, verbose=False, plotFit=False)
            fit_vals = pd.concat((fit_vals, fit_params['value']), axis=1)
            fit_errs = pd.concat((fit_errs, fit_params['err']), axis=1)
            fit_chisqrs += [chisqr]
            
        fit_vals.columns = ty
        fit_vals = fit_vals.swapaxes('index', 'columns')
        fit_errs.columns = ty
        fit_errs = fit_errs.swapaxes('index', 'columns')
        fit_chisqrs = pd.Series(data=fit_chisqrs, index=ty)
    elif fit_ax=='y': # Fit along vertical
        
        
        fit_params, _, _, _, _, chisqr = do_fit(ty, timg[:, 0], model_func, guess_func, 
                                                params=params, verbose=False, plotFit=False)
        fit_vals = fit_params['value']
        fit_errs = fit_params['err']
        fit_chisqrs = [chisqr]
        for i in range(1, timg.shape[1]):
            if mode=='sequential':
                newguess = fitted_to_params(fit_params)
            else:
                # Doing minner.minimize() will not change the input params
                newguess = params
            fit_params, _, _, _, _, chisqr = do_fit(ty, timg[:, i], model_func, guess_func, 
                                                params=newguess, verbose=False, plotFit=False)
            fit_vals = pd.concat((fit_vals, fit_params['value']), axis=1)
            fit_errs = pd.concat((fit_errs, fit_params['err']), axis=1)
            fit_chisqrs += [chisqr]
            
        fit_vals.columns = tx
        fit_vals.swapaxes('index', 'columns')
        fit_errs.columns = tx
        fit_errs.swapaxes('index', 'columns')
        fit_chisqrs = pd.Series(data=fit_chisqrs, index=tx)
        
    if plotFit:
        pNum = fit_vals.shape[1]+1
        color=iter(cm.rainbow(np.linspace(0,1,pNum)))
        fig, frame_ax = plt.subplots(pNum, 1, sharex=True, figsize=(5, 1.5*pNum))
        for j, key in enumerate(fit_vals.columns):
            frame_ax[j].errorbar(fit_vals.index, fit_vals[key], yerr=fit_errs[key], 
                                 color=next(color), marker='.')
            frame_ax[j].set_ylabel(key)
            
        frame_ax[pNum-1].plot(fit_chisqrs, color=next(color), marker='.')
        frame_ax[pNum-1].set_ylabel('chisq')
    
    return fit_vals, fit_errs, fit_chisqrs


#==============================================================================
# Fitting procedures
# Fermi edge
#==============================================================================


def FermiLinearBG(params, x, y):
    '''
    Fermi func with linear BG
    '''
    Ef = params['Ef']
    T = params['T']
    A = params['Slope']
    B = params['Intercept']
    BG = params['Offset']
        
    model = BG+A*(x-B)/(np.exp((x-Ef)/kB/T)+1)
    return model-y


def guess_FermiLinearBG(x, y):
    '''
    Making initial guess
    '''
    BG = np.nanmin(y)
    Ef = x[np.nanargmax(np.absolute(np.gradient(y)))]
    
    # Usual ARPES data is taken no higher than 450 K
    # 4*k_B*T = 150 meV at 450 K
    # Usual ARPES data will go at least 200 meV below Ef
    
    E1 = x[np.nanargmin(x)]
    E2 = x[np.nanargmin((x-Ef-0.2)**2)]
    C1 = y[np.nanargmin(x)]
    C2 = y[np.nanargmin((x-Ef-0.2)**2)]
    Slope = (C2-C1)/(E2-E1)
    Intercept = E2-(C2-BG)/Slope
    
    params = Parameters()
    params.add('Ef', value=Ef)
    params.add('T', value=30., min=2.)
    params.add('Slope', value=Slope)
    params.add('Intercept', value=Intercept)
    params.add('Offset', value=BG)
    
    return params


