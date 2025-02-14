#==============================================================================
# imports
#==============================================================================
import math
import numpy as np
import matplotlib.pyplot as plt
import ast
from scipy import interpolate

#==============================================================================
# Global variables in science
#==============================================================================

kB = 8.6173423e-05          # Boltzmann k in eV/K
me = 5.68562958e-32         # Electron mass in eV*(Angstroms^(-2))*s^2
hbar = 6.58211814e-16       # hbar in eV*s
hc_over_e = 12.3984193      # hc/e in keV⋅A
hc_e = 1239.84193           # hc/e in eV*A

#==============================================================================
# functions to convert to and from k-space
#==============================================================================

def theta_to_kx(KE, thetaX):
    '''
    thetaX = polar angle
    kx = c*sqrt(KE)*sin(thetaX)
    '''

    c = np.sqrt(2*me)/hbar
    kx = c*np.sqrt(KE)*np.sin(thetaX*np.pi/180.)

    return kx


def theta_to_ky(KE, thetaX, thetaY):
    '''
    thetaX = polar angle
    thetaY = other angle
    ky = c*sqrt(KE)*cos(thetaX)*sin(thetaY)
    '''
    c = np.sqrt(2*me)/hbar
    ky = c*np.sqrt(KE)*np.cos(thetaX*np.pi/180.)*np.sin(thetaY*np.pi/180.)
    
    return ky


def theta_to_kz(KE, thetaX, thetaY, V0=10):
    '''
    thetaX = polar angle
    thetaY = other angle
    V0=inner potential
    kz = c*sqrt(V0-KE*(sin(thetaX)+cos(thetaX)*sin(thetaY)+1))
    '''
    c = np.sqrt(2*me)/hbar
    kz = c*np.sqrt(V0-KE*(np.sin(thetaX)+np.cos(thetaX)*np.cos(thetaY)+1)) #equation is probably wrong JM look into this

    return kz
    

def k_to_thetaX(KE, kx):
    '''
    
    '''
    
    c = np.sqrt(2*me)/hbar
    thetaX = np.arcsin(kx/(c*np.sqrt(KE)))
    
    return thetaX

def k_to_thetaY(KE, kx, ky):
    '''
    
    '''
    
    c = np.sqrt(2*me)/hbar
    thetaY = np.arcsin(ky/(c*np.sqrt(KE)*np.cos(np.arcsin(kx/(c*np.sqrt(KE))))))
    
    return thetaY

def k_to_kz(kx, ky, KE, V0):
    """
    """
    c = np.sqrt(2*me)/hbar
    kz2 = c**2*(KE - V0) - (kx**2 +ky**2)
    return np.sqrt(kz2)

def KE_to_BE(KE,hv,wk):  
    ''''''
    BE = hv-wk-KE 
    return BE

def BE_to_KE(BE, hv, wk):
    ''''''
    KE = hv-wk-BE 
    return KE
    
def ARPES_angle_k(k_new,img,KE_scale,angle_scale,polar_angle,KE_offset,slit='V'):
    """
    k_new = interpolated k scaling (slitV => ky, slitH => kx)
    
    img = data image for slitH =>(KE,angle); slitV =>(angle,KE)
    KE_scale = Kinetic energy scaling for img
    angle scale = of image (slitV => thetaY, slitH => thetaX)

    polar_angle =  polar angle of manipulator (for slitH then added to detector angle)
    KE_offset = to adjust for Fermi level drift (can be float, or np.array of the same length as the image )
    slit = slit direction: 'V' or 'H'
    
    Currently only works for E_new = KE_scale
    """
    img_new = np.empty((angle_scale.shape[0],KE_scale.shape[0]))
    
    for j,KE in enumerate(KE_scale):
        
        if slit == 'H':
            y = img[j,:] #Intensity vs ThetaX
            x = theta_to_kx(KE+KE_offset,polar_angle+angle_scale)
        elif slit == 'V':
            y = img[:,j] #Intensity vs ThetaY
            x = theta_to_ky(KE+KE_offset,polar_angle,angle_scale) #converting thetaY to ky units
        else:
            print('slit needs to be "H" or "V"')
            return 
        
        f = interpolate.interp1d(x,y,bounds_error=False, fill_value=np.nan)
        x_new = k_new
        y_new = f(x_new)
        if slit == 'H':
            img_new[j,:] = y_new
        elif slit == 'V':    
            img_new[:,j] = y_new
        
    return img_new