from math import sqrt
import numpy as np
import numpy.polynomial.polynomial as poly
from numpy import log as ln
from scipy.optimize import curve_fit
from scipy.special import erfc
import matplotlib.pyplot as plt
import lmfit

from iexplot.plotting import plot_1D
from iexplot.plotting import find_closest   #index, value

def _xrange(x,y,xrange=[np.inf,np.inf]):
    """
    xrange = [first_x_val, last_x_val]
    return x_sub and y_sub over a range defined xrange so that x_sub is increasing
    """
    if xrange[0] == np.inf:
        x_first = x[0]
    else: 
        x_first = xrange[0]

    if xrange[1] == np.inf:
        x_last = x[-1]
    else: 
        x_last = xrange[1]


    first_index, first_value = find_closest(x,x_first)
    last_index, last_value   = find_closest(x,x_last)

    if first_index < last_index:
        x_sub = x[first_index:last_index]
        y_sub = y[first_index:last_index]
    else:
        x_sub = x[last_index:first_index]
        y_sub = y[last_index:first_index]
        
    return x_sub, y_sub

def gaussian(x,*coefs):
    """
    Function for a guassian
    coefs = [A,x0,sigma,bkgd]
    returns f(x) = bkgd + A*numpy.exp(-(x-x0)**2/(2.*sigma**2)
    fwhm=2.355*sigma
    """
    A, x0, sigma, bkgd = coefs
    return bkgd + A*np.exp(-(x-x0)**2/(2.*sigma**2))

def fit_gaussian(x,y,**kwargs):
    """
    fits a gaussian and returns fit_x, fit_y, coefs, covar 

    x,y np.arrays of the the x,y data

    **kwargs:
        plot: True/False plots the data and the fit (default=True)
        xrange=[x_first,x_last] to fit subrange 
        coefs_0=[Amplitude,x0,sigma,bkgd] to specifiy initial guesses, otherwise autoguess

    Usage examples:
        x,y = EA_Spectrum(ScanNum,EnergyAxis)
        x,y,x_name,y_name = mda_1D(ScanNum,detNum)

    """
    kwargs.setdefault('plot',True)
    kwargs.setdefault('xrange',[np.inf,np.inf])

    #subrange
    x_fit, y_fit = _xrange(x,y,kwargs['xrange'])
    
    #initial guess using subranges if not specified in kwargs
    A = np.max(y_fit)
    x0 = x_fit[np.where(y_fit==A)[0][0]]       #first point where y == max value
    x1 = x_fit[find_closest(y_fit,A/2)[0]] #x point where half intensity
    sigma = abs(x1-x0)/2
    bkgd = np.mean(y_fit)
    coefs_0 = [A, x0, sigma, bkgd] if 'coefs_0' not in kwargs else kwargs['coefs_0']

    coefs, covar = curve_fit(gaussian, x_fit, y_fit, coefs_0)
    y_fit= gaussian(x_fit, *coefs)
    fit_vals = {
        'Amp':coefs[0],
        'center':coefs[1],
        'FWHM':sqrt(8*ln(2))*coefs[2]
        }

    if kwargs['plot']:
        _plot_fit(x,y,x_fit,y_fit,fit_vals,**kwargs)

    return x_fit,y_fit,coefs,covar,fit_vals


def _lorentzian(x,*coefs):
    """
    Function for a lorentzian
    coefs = [A,x0,sig,bkgd] 
    f(x) = bkgd + Gamma/2/np.pi / ((x-x0)**2+(Gamma/2)**)

    """
    A, x0, sig, bkgd =coefs
    #return bkgd + A*Gamma**2/(Gamma**2+(x-x0)**2)
    return bkgd + A/np.pi * sig / ((x-x0)**2+(sig)**2)

def fit_lorentzian(x,y,**kwargs):
    """
    fits a lorentzian and returns fit_x, fit_y, coefs, covar 

    x,y np.arrays of the the x,y data

    **kwargs:
        plot: True/False plots the data and the fit (default=True)
        xrange=[x_first,x_last] to fit subrange 
        coefs_0=[Amplitude,x0,sigma,bkgd] to specifiy initial guesses, otherwise autoguess

    Usage examples:
        x,y = EA_Spectrum(ScanNum,EnergyAxis)
        x,y,x_name,y_name = mda_1D(ScanNum,detNum)

    """
    kwargs.setdefault('plot',True)
    kwargs.setdefault('xrange',[np.inf,np.inf])

    #subrange
    x_fit, y_fit = _xrange(x,y,kwargs['xrange'])
    
    #initial guess using subranges if not specified in kwargs
    A = np.max(y_fit)
    x0 = x_fit[np.where(y_fit==A)[0][0]]      #first point where y == max value
    x1 = x_fit[find_closest(y_fit,A/2)[0]] #x point where half intensity
    sigma = abs(x1-x0)/2
    bkgd = np.mean(y_fit)
    coefs_0 = [A, x0, sigma, bkgd] if 'coefs_0' not in kwargs else kwargs['coefs_0']


    coefs, covar = curve_fit(_lorentzian, x_fit, y_fit, coefs_0)
    y_fit= _lorentzian(x_fit, *coefs)
    fit_vals = {
        'Amp':coefs[0],
        'center':coefs[1],
        'FWHM':sqrt(8*ln(2))*coefs[2]
        }

    if kwargs['plot']:
        _plot_fit(x,y,x_fit,y_fit,fit_vals,**kwargs)

    return  x_fit,y_fit,coefs,covar,fit_vals


def _step(x,*coefs):
    """
    Function for a step/error
    p = [A,x0,width,bkgd]
    returns f(x) = bkgd + A*erfc((x -x0)/width) 
    """
    A, x0, width, bkgd = coefs
    return bkgd + A*erfc((x -x0)/width) 

def fit_step(x,y,**kwargs):
    """
    fits a lorentzian and returns fit_x, fit_y, coefs, covar 

    x,y np.arrays of the the x,y data

    **kwargs:
        plot: True/False plots the data and the fit (default=True)
        xrange=[x_first,x_last] to fit subrange 
        coefs_0=[Amplitude,x0,sigma,bkgd] to specifiy initial guesses, otherwise autoguess

    Usage examples:
        x,y = EA_Spectrum(ScanNum,EnergyAxis)
        x,y,x_name,y_name = mda_1D(ScanNum,detNum)

    """
    kwargs.setdefault('plot',True)
    kwargs.setdefault('xrange',[np.inf,np.inf])

    #subrange
    x_fit, y_fit = _xrange(x,y,kwargs['xrange'])
    
    #initial guess using subranges if not specified in kwargs
    A = np.mean(np.sign(np.array(y_fit)))*(np.max(y_fit)-np.min(y_fit))/2 #step height
    x0 = x_fit[find_closest(y_fit,np.mean(y_fit))[0]] #x point where mean intensity
    x1 = x_fit[find_closest(y_fit,1.25*np.mean(y_fit))[0]] #x point where 1.25 mean intensity
    width = abs(x1-x0)
    bkgd = np.min(y_fit) 

    coefs_0 = [A, x0, width, bkgd] if 'coefs_0' not in kwargs else kwargs['coefs_0']

    coefs, covar = curve_fit(_step, x_fit, y_fit, coefs_0)
    y_fit= _step(x_fit, *coefs)
    fit_vals={
        'height':coefs[0],
        'center':coefs[1],
        'width':coefs[2],
    }

    if kwargs['plot']:
        _plot_fit(x,y,x_fit,y_fit,fit_vals,**kwargs)

    return  x_fit,y_fit,coefs,covar,fit_vals


def fit_voigt(x,y,**kwargs):
    kwargs.setdefault('plot',True)
    kwargs.setdefault('xrange',[np.inf,np.inf])
    
    #subrange
    x, y = _xrange(x,y,kwargs['xrange'])    
    
    model = lmfit.models.VoigtModel()
    params = model.guess(y,x=x)
    
    y_fit = model.fit(y,params, x=x)
    
    if kwargs['plot']:
        _plot_fit(x,y,x,y_fit.best_fit,**kwargs)
    
    return y_fit

def _box(x, *p):
    """
    Function for a box (double step)
    p = [A,x0,width,bkgd]
    returns f(x) = bkgd + A*((x0 - width/2) < x)*(x < (x0 + width/2))
    """
    A, x0, width, bkgd = p
    return bkgd + A*((x0 - width/2) < x)*(x < (x0 + width/2))


def fit_box(x,y,**kwargs):
    """
    fits a box and returns fit_x, fit_y, coefs, covar 

    x,y np.arrays of the the x,y data

    **kwargs:
        plot: True/False plots the data and the fit (default=True)
        xrange=[x_first,x_last] to fit subrange 
        coefs_0=[Amplitude,x0,sigma,bkgd] to specifiy initial guesses, otherwise autoguess

    Usage examples:
        x,y = EA_Spectrum(ScanNum,EnergyAxis)
        x,y,x_name,y_name = mda_1D(ScanNum,detNum)

    """
    kwargs.setdefault('plot',True)
    kwargs.setdefault('xrange',[np.inf,np.inf])

    #subrange
    x_fit, y_fit = _xrange(x,y,kwargs['xrange'])
    
    #initial guess using subranges if not specified in kwargs
    A = np.mean(np.sign(np.array(y_fit)))*(np.max(y_fit)-np.min(y_fit))/2 #step hight
    x0 = x_fit[find_closest(y_fit,np.mean(y_fit))[0]] #x point where mean intensity
    x1 = x_fit[find_closest(y_fit,1.25*np.mean(y_fit))[0]] #x point where 1.25 mean intensity
    sigma = abs(x1-x0)/2
    bkgd = np.min(y_fit) 

    coefs_0 = [A, x0, sigma, bkgd] if 'coefs_0' not in kwargs else kwargs['coefs_0']

    coefs, covar = curve_fit(_box, x_fit, y_fit, coefs_0)
    y_fit= _box(x_fit, *coefs)
    fit_vals={
        'height':coefs[0],
        'center':coefs[1],
        'width':coefs[2],
    }

    if kwargs['plot']:
        _plot_fit(x,y,x_fit,y_fit,fit_vals,**kwargs)

    return  x_fit,y_fit,coefs,covar,fit_vals

def fit_poly(x,y,rank=3,**kwargs):
    """
    fits a box and returns fit_x, fit_y, coefs, covar 

    x,y np.arrays of the the x,y data

    **kwargs:
        plot: True/False plots the data and the fit (default=True)
        xrange=[x_first,x_last] to fit subrange 
        coefs_0=[Amplitude,x0,sigma,bkgd] to specifiy initial guesses, otherwise autoguess

    Usage examples:
        x,y = EA_Spectrum(ScanNum,EnergyAxis)
        x,y,x_name,y_name = mda_1D(ScanNum,detNum)

    """
    kwargs.setdefault('plot',True)
    kwargs.setdefault('xrange',[np.inf,np.inf])

    #subrange
    x_fit, y_fit = _xrange(x,y,kwargs['xrange'])
    
    coefs = poly.polyfit(x, y, rank)
    y_fit = poly.polyval(x_fit, coefs)
    fit_vals={}
    for i,c in enumerate(coefs):
        fit_vals.update({'c'+str(i):c})
    if kwargs['plot']:
        _plot_fit(x,y,x_fit,y_fit,**kwargs)

    return  x_fit,y_fit,coefs,None,fit_vals



def _plot_fit(x,y,x_fit,y_fit,fit_vals={},**kwargs):
    """
    appends data and fit
    **kwargs:
        data_label: default='data'
        fit_label: default = 'fit'
    """
    kwargs.setdefault('data_label','data')
    kwargs.setdefault('fit_label','fit')
    data_label = kwargs['data_label']
    kwargs.pop('data_label')
    fit_label = kwargs['fit_label']
    kwargs.pop('fit_label') 
    print(kwargs)

    txt=""
    for i,key in enumerate(fit_vals.keys()):
        txt+=key+": "+"{:.4e}".format(fit_vals[key])+"\n"

    for key in ['marker','color']:
        if key in kwargs.keys():
            kwargs.pop(key)
    plt.plot(x,y,label=data_label,marker='x',color='k')
    plt.plot(x_fit,y_fit,label=fit_label,color='r')
    plt.plot([], [], ' ', label=txt[:-1])
    plt.legend()
    plt.show()

def find_EF_offset(EA_list, E_unit,fit_type,xrange, plot = False):
        '''
        finds and applies the Fermi level offset for each scan in EA_list
        
        EA_list = list of EA scans 
        E_unit = KE or BE
        fit_type = function to fit data to, 'step' or 'Voigt'
        xrange = subrange of each scan to be fit
        '''
        
        f = {}
        cen = list()
        for i, EA in enumerate(EA_list):
            if E_unit == 'BE':
                x = EA.BEscale
            else:
                x = EA.KEscale
                
            y = EA.EDC.data
            if fit_type == 'step':
                fi = fit_step(x,y,xrange=xrange, plot=plot)
                f[i] = fi
                cen.append(fi[2][1])
            elif fit_type == 'Voigt':
                fi = fit_voigt(x,y,xrange=xrange, plot=plot)
                f[i] = fi
                cen.append(fi.params['center'].value)
            else:
                print(fit_type + 'is not a valid fitting function, see doc string')
                
        return np.array(cen)