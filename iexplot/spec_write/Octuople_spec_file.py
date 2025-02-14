#Functions for reading and analyzing 29-ID data
# J.W. Freeland(APS/ANL)  Updated 7/12/22
# Thanks to Yue Cao (ANL) for the functions for reading spec files

import os
import sys
import glob
import h5py
import time
import numpy as np
import pandas as pd

from iexplot.mda import readMDA

def Octupole_get_data(scanNum,path,**kwargs):
    """
    returns mda file data

    **kwargs:
        'prefix' => "Kappa_"
        'suffix_format' => '{:04}.mda'
    """
    kwargs.setdefault('prefix',"Octupole_")
    kwargs.setdefault('suffix_format','{:04}.mda')

    if path[-1]=="/":
        sf = path + kwargs['prefix']
    else:
        sf = path +"/"+ kwargs['prefix']
    data=readMDA(sf+kwargs['suffix_format'].format(scanNum))

def Octuople_detectors(scanNum,path,**kwargs):
    """
    returns dictionary of detector locations in mda file
    filepath = path + prefix + filenum + suffix

    """
    data = Octupole_get_data(scanNum,path,**kwargs)

    detnames = []
    for i in range(0,data[1].nd):
        detnames.append(data[1].d[i].name)
    detnames =  np.array(detnames)

    det_dict = {'TEYn':'29ide:scaler1_calc3.VAL'}
    det_dict['MCPn'] = '29ide:scaler1_calc4.VAL'
    det_dict['PDn'] = '29ide:scaler1_calc5.VAL'
    det_dict['Dn'] = '29ide:scaler1_calc6.VAL'
    det_dict['TFYn'] = '29ide:userTran3.D'
    det_dict['PFYn'] = '29ide:userTran3.E'
    det_dict['i0'] = '29ide:scaler1.S2'
    det_dict['TEYr'] = '29ide:scaler1.S3'
    det_dict['MCPr'] = '29ide:scaler1.S4'
    det_dict['PDr'] = '29ide:scaler1.S5'
    det_dict['Dr'] = '29ide:scaler1.S6'
    det_dict['TFYr'] = '29idVORTEX:mca1.R0'
    det_dict['PFYr'] = '29idVORTEX:mca1.R1'
    det_dict['TEY_sum'] = '29ide:userTran3.I'
    det_dict['TFY_sum'] = '29ide:userTran3.J'
    det_dict['PD_sum'] = '29ide:userTran3.K'
    det_dict['XMCD_TEY'] = '29ide:userTran3.L'
    det_dict['XMCD_TFY'] = '29ide:userTran3.M'
    det_dict['XMCD_PD'] = '29ide:userTran3.N'

    det_loc = {}
    det_loc['TEYn'] = np.where(detnames==det_dict['TEYn'])[0][0]
    det_loc['MCPn'] = np.where(detnames==det_dict['MCPn'])[0][0]
    det_loc['PDn'] = np.where(detnames==det_dict['PDn'])[0][0]
    det_loc['Dn'] = np.where(detnames==det_dict['Dn'])[0][0]
    if len(np.where(detnames==det_dict['TFYn'])[0]) != 0:
        det_loc['TFYn'] = np.where(detnames==det_dict['TFYn'])[0][0]
        det_loc['PFYn'] = np.where(detnames==det_dict['PFYn'])[0][0]
    det_loc['i0'] = np.where(detnames==det_dict['i0'])[0][0]
    det_loc['TEYr'] = np.where(detnames==det_dict['TEYr'])[0][0]
    det_loc['MCPr'] = np.where(detnames==det_dict['MCPr'])[0][0]
    det_loc['PDr'] = np.where(detnames==det_dict['PDr'])[0][0]
    det_loc['Dr'] = np.where(detnames==det_dict['Dr'])[0][0]
    if len(np.where(detnames==det_dict['TEY_sum'])[0]) != 0:
        det_loc['TEY_sum'] = np.where(detnames==det_dict['TEY_sum'])[0][0]
        det_loc['TFY_sum'] = np.where(detnames==det_dict['TFY_sum'])[0][0]
        det_loc['PD_sum'] = np.where(detnames==det_dict['PD_sum'])[0][0]
        det_loc['XMCD_TEY'] = np.where(detnames==det_dict['XMCD_TEY'])[0][0]
        det_loc['XMCD_TFY'] = np.where(detnames==det_dict['XMCD_TFY'])[0][0]
        det_loc['XMCD_PD'] = np.where(detnames==det_dict['XMCD_PD'])[0][0]
    if (np.where(detnames==det_dict['TFYn'])[0]) != 0:
        det_loc['TFYr'] = np.where(detnames==det_dict['TFYr'])[0][0]
        det_loc['PFYr'] = np.where(detnames==det_dict['PFYr'])[0][0]

    return det_loc

def Octupole_scantype(scanNum,path,**kwargs):
    """
    returns string of scanType
    
    filepath = path + prefix + filenum + suffix
    """
    data = Octupole_get_data(scanNum,path,**kwargs)

    pos_dict = {'energy':'29idmono:ENERGY_SP'}
    pos_dict['x'] = '29ide:m11.VAL'
    pos_dict['y'] = '29ide:m12.VAL'
    pos_dict['z'] = '29ide:m13.VAL'
    pos_dict['th'] = '29ide:m14.VAL'
    pos_dict['tth'] = '29ide:m15.VAL'
    pos_dict['hys'] = '29ide:userTran5.D'

    try:
        posname = (data[1].p[0].name)
        pos_start = round(data[1].p[0].data[0])
        pos_end = round(data[1].p[0].data[-1])
        pos_unit = data[1].p[0].unit
        scantype = list(pos_dict.keys())[list(pos_dict.values()).index(posname)]

    except:
        posname = 'none'
        pos_start = 'none'
        pos_end = 'none'
        pos_unit = 'none'
        scantype = 'Unknown scan'
            
    return scantype + ' scan ' + str(pos_start)+' - '+str(pos_end) + ' ' + pos_unit

def Octuople_scan_details(scanNum,path,**kwargs):
    data = Octupole_get_data(scanNum,path,**kwargs)

    sample_dict = {'x':'29ide:m11.VAL'}
    sample_dict['y'] = '29ide:m12.VAL'
    sample_dict['z'] = '29ide:m13.VAL'
    sample_dict['th'] = '29ide:m14.VAL'
    sample_dict['tth'] = '29ide:m15.VAL'
    sample_dict['energy'] = '29idmono:ENERGY_MON'
    sample_dict['TA'] = '29ide:LS340:LS340_1:Control'
    sample_dict['pol'] = 'ID29:ActualMode'
    print('Scan number: ',scanNum)
    for key in sample_dict:
        header = data[0][sample_dict[key]]
        print(header[0]+ ': ' + str(header[2][0])+' '+header[1])
            
def Octuople_scan_energy(scanNum,path,**kwargs):
    data = Octupole_get_data(scanNum,path,**kwargs)
    header = data[0]['29idmono:ENERGY_MON']
    
    return header[2][0]
        
def Octupole_scan_detail_list(scanNum,path,**kwargs):
    """
    returns spec string
    """
    kwargs('prefix',"Octupole_")
    kwargs('suffix_format','{:04}.mda')
    data = Octupole_get_data(scanNum,path,**kwargs)
    
    sample_dict = {'x':'29ide:m11.VAL'}
    sample_dict['y'] = '29ide:m12.VAL'
    sample_dict['z'] = '29ide:m13.VAL'
    sample_dict['th'] = '29ide:m14.VAL'
    sample_dict['tth'] = '29ide:m15.VAL'
    sample_dict['energy'] = '29idmono:ENERGY_MON'
    sample_dict['TA'] = '29ide:LS340:LS340_1:Control'
    sample_dict['pol'] = 'ID29:ActualMode'
    energy  = data[0][sample_dict['energy']]
    TA = data[0][sample_dict['TA']]
    pol = data[0][sample_dict['pol']]

    try:
        return 'E({}): {:.1f} T(K): {:.1f} pol: {} th: {} tth: {}'.format(energy[1],energy[2][0],TA[2][0],pol[2].split(',')[1],)
    except:
        return 'E({}): {:.1f} T(K): {:.1f} pol: {}'.format(energy[1],energy[2][0],TA[2][0],pol[2])

def Octupole_scan_dims(scanNum,path,**kwargs):
    data = Octupole_get_data(scanNum,path,**kwargs)
    scan_dims=int(data[0]['acquired_dimensions'][0]) #using table scan writes full array
    return scan_dims