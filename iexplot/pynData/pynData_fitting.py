
import numpy as np

from iexplot.fitting import fit_box,fit_gaussian,fit_lorentzian,fit_poly,fit_step
from iexplot.plotting import plot_1D
from iexplot.pynData.pynData_plot import plot_nd

#Fitting function for pynData

def fit_nd(nd,fit_type,**kwargs):
    """
    for each x value fits Int(y) and 
    returns x_fit,y_fit,coefs,covar,fit_vals 
    
    nd is a pndata object (such as EA_stack or data.mda_det[detNum])
    fit_type = 'box','gaussian','lorentzian','poly','step'
    
    **kwargs
        xrange=[y_first,y_last] to fit subrange 
        plot_fits1D = True/False (default = False), line profiles + fits
        plot_fits2D = True/False (default = False), image + center
        
        show_legend = True/False (default = False)
        see fit_box, fit_gaussian... for other kwargs   
    fit_vals = dictionary of arrays with dict_keys(['Amp', 'center', 'FWHM'])      
    """
    kwargs.setdefault('plot_fits1D',False)
    kwargs.setdefault('show_legend',False)
    
    fit_funcs = {
        'box':fit_box,
        'gaussian':fit_gaussian,
        'lorentzian':fit_lorentzian,
        'poly':fit_poly,
        'step:':fit_step,
    }
    if fit_type not in fit_funcs.keys():
        print('Not a valid fit_type use one of the following'+list(fit_funcs.keys()) )
        #return
    
    fit_func = fit_funcs[fit_type]
    x_fit,y_fit,coefs,covar,fit_vals  = fit_func(nd.scale['x'],nd.data,**kwargs)
   
    return x_fit,y_fit,coefs,covar,fit_vals 


def fit_nd_stack(nd,fit_type,**kwargs):
    """
    for each y value fits Int(x) and 
    returns x_fit,y_fit,coefs,covar,fit_vals 
    
    nd is a pndata object (such as EA_stack or data.mda_det[detNum])
    fit_type = 'box','gaussian','lorentzian','poly','step'
    
    **kwargs
        xrange=[x_first,x_last] to fit subrange 
        plot_fits1D = True/False (default = False), line profiles + fits
        plot_fits2D = True/False (default = True), image + center
        
        show_legend = True/False (default = False)
        see fit_box, fit_gaussian... for other kwargs

    fit_vals = dictionary of arrays with dict_keys(['Amp', 'center', 'FWHM'])      
    """
    kwargs.setdefault('plot_fits1D',False)
    kwargs.setdefault('show_legend',False)
    kwargs.setdefault('plot_fits2D',True)

    if kwargs['plot_fits1D']:
        kwargs.update({'plot':True})
    else:
        kwargs.update({'plot':False})
    kwargs.pop('plot_fits1D',None)

    
    fit_funcs = {
        'box':fit_box,
        'gaussian':fit_gaussian,
        'lorentzian':fit_lorentzian,
        'poly':fit_poly,
        'step:':fit_step,
    }
    if fit_type not in fit_funcs.keys():
        print('Not a valid fit_type use one of the following'+list(fit_funcs.keys()) )
        #return
    
    fit_func = fit_funcs[fit_type]

    for j,y in enumerate(nd.scale['y']):
        ff = fit_func(nd.scale['x'],nd.data[j,:],**kwargs)
        if j == 0:
            x_fit,y_fit,coefs,covar,fit_vals = ff
            for key in fit_vals.keys():
                fit_vals[key]=np.array(fit_vals[key])
        else:           
            x_fit = np.vstack((x_fit,ff[0]))
            y_fit = np.vstack((y_fit,ff[1]))
            coefs = np.vstack((coefs,ff[2]))
            covar = np.dstack((covar,ff[3]))
            for key in fit_vals.keys():
                fit_vals[key] = np.vstack((fit_vals[key],ff[4][key]))
    
    if kwargs['plot_fits2D']:
        plot_nd(nd)
        plot_1D(fit_vals['center'],nd.scale['y'],marker='x',color='red',linestyle='None')
    
    return x_fit,y_fit,coefs,covar,fit_vals