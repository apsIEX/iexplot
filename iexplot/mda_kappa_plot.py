
import matplotlib.pyplot as plt
import numpy as np

from iexplot.mda_quick_plot import plot_mda,fit_mda

try:
    import iexcode.instruments.cfg as iex
    from iexcode.instruments.scanRecord import last_mda

except:
    print('need to specify det_name')

def kappa_detNum(det_name,norm2mesh=False):
    """
    returns the detector number for det_name
    det_name: detector name e.g. 'd3' / 'd4' / 'tey' /'mcp
    norm2mesh: True/False scaler valued divided by mesh or raw
    """
    if norm2mesh:
        key = det_name+"_norm"
    else:
        key = det_name
    det_dict = {
        'mesh':31,
        'tey':32,
        'd3':33,
        'd4':34,
        'mcp':35,
        'tey_norm':36,
        'd3_norm':37,
        'd4_norm':38,
        'mcp_norm':39,
    }
    return det_dict[key]


def fit_d4(scanNum=last_mda(),detNum=34): 
    """
    fits a gauss to last scan for d4 
    """   
    d4=fit_mda(scanNum,detNum,'gauss',title='mda_'+str(scanNum).zfill(4))  
    return round(d4,3)

def fit_d3(scanNum=last_mda(),detNum=33):
    d3=fit_mda(scanNum,detNum,'gauss',title='mda_'+str(scanNum).zfill(4))  
    return round(d3,3)

def fit_z(scanNum=last_mda(),detNum=33):
    z=fit_mda(scanNum,detNum,'erf',title='mda_'+str(scanNum).zfill(4))  
    return round(z,0)
    
def plot_last():
    """
    plots last scan in kappa for detector
    needs work, 
    """
    if iex.BL.endstation_name.lower() == 'kappa':
        try:
            scanNum=last_mda()
            detNum=kappa_detNum(det_name=iex.det.get(),norm2mesh=False)
            plot_mda(scanNum,detNum,title='mda_'+str(scanNum).zfill(4))  
        except:
            print('error')
    else:
        print('Function only defined for kappa')
    
     
def Find_kth_zero(th_0,th_180):
    """
    th_0 is the motor position for specular near zero 
    th_180 is motor position for spectular near 180 
    """
    
    Offset =0.5*(180 - th_180 - th_0)

    print("with motor at 0, the actual value is ",Offset)
    