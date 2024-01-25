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

def Kappa_get_data(scanNum,path,**kwargs):
    """
    returns mda file data

    **kwargs:
        'prefix' => "Kappa_"
        'suffix_format' => '{:04}.mda'
    """
    kwargs.setdefault('prefix',"Kappa_")
    kwargs.setdefault('suffix_format':'{:04}.mda')

    if path[-1]=="/":
        sf = path + prefix
    else:
        sf = path +"/"+ prefix
    data=readMDA(sf+suffix_format.format(scanNum))
    return data

def Kappa_detectors(scanNum,path,**kwargs):
    """
    returns dictionary of detector locations in mda file
    filepath = path + prefix + filenum + suffix

    """
    data = Kappa_get_data(scanNum,path)

    detnames = []
    for i in range(0,data[1].nd):
        detnames.append(data[1].d[i].name)
    detnames =  np.array(detnames)

    det_dict = {'TEYn':'29idMZ0:scaler1_calc1.B'}
    det_dict['d3n'] = '29idMZ0:scaler1_calc1.C'
    det_dict['d4n'] = '29idMZ0:scaler1_calc1.D'
    det_dict['MCPn'] = '29idMZ0:scaler1_calc1.E'
    det_dict['TFYn'] = '29idd:userTran1.D'
    det_dict['PFYn'] = '29idd:userTran1.E'
    det_dict['i0'] = '29idMZ0:scaler1.S14'
    det_dict['TEYr'] = '29idMZ0:scaler1.S2'
    det_dict['d3r'] = '29idMZ0:scaler1.S3'
    det_dict['d4r'] = '29idMZ0:scaler1.S4'
    det_dict['MCPr'] = '29idMZ0:scaler1.S5'
    det_dict['TFYr'] = '29idVORTEX:mca1.R0'
    det_dict['PFYr'] = '29idVORTEX:mca1.R1'
    det_dict['H'] = '29idKappa:userArrayCalc1.L'
    det_dict['K'] = '29idKappa:userArrayCalc2.L'
    det_dict['L'] = '29idKappa:userArrayCalc3.L'
    det_dict['T'] = '29idd:LS331:TC1:SampleA'
    det_loc = {}
    if len(np.where(detnames==det_dict['H'])[0]) != 0:
        det_loc['H'] = np.where(detnames==det_dict['H'])[0][0]
        det_loc['K'] = np.where(detnames==det_dict['K'])[0][0]
        det_loc['L'] = np.where(detnames==det_dict['L'])[0][0]
    det_loc['TEYn'] = np.where(detnames==det_dict['TEYn'])[0][0]
    det_loc['d3n'] = np.where(detnames==det_dict['d3n'])[0][0]
    det_loc['d4n'] = np.where(detnames==det_dict['d4n'])[0][0]
    det_loc['MCPn'] = np.where(detnames==det_dict['MCPn'])[0][0]
    if len(np.where(detnames==det_dict['TFYn'])[0]) != 0:
        det_loc['TFYn'] = np.where(detnames==det_dict['TFYn'])[0][0]
        det_loc['PFYn'] = np.where(detnames==det_dict['PFYn'])[0][0]
    det_loc['i0'] = np.where(detnames==det_dict['i0'])[0][0]
    det_loc['TEYr'] = np.where(detnames==det_dict['TEYr'])[0][0]
    det_loc['d3r'] = np.where(detnames==det_dict['d3r'])[0][0]
    det_loc['d4r'] = np.where(detnames==det_dict['d4r'])[0][0]
    det_loc['MCPr'] = np.where(detnames==det_dict['MCPr'])[0][0]
    if (np.where(detnames==det_dict['TFYn'])[0]) != 0:
        det_loc['TFYr'] = np.where(detnames==det_dict['TFYr'])[0][0]
        det_loc['PFYr'] = np.where(detnames==det_dict['PFYr'])[0][0]
    det_loc['T'] = np.where(detnames==det_dict['T'])[0][0]

    return det_loc

def Kappa_scan_type(scanNum,path,**kwargs):
    """
    returns string of scanType

    filepath = path + prefix + filenum + suffix
    """
    data = Kappa_get_data(scanNum,path,**kwargs)

    pos_dict = {'energy':'29idmono:ENERGY_SP'}
    pos_dict['x'] = '29idKappa:m2.VAL'
    pos_dict['y'] = '29idKappa:m3.VAL'
    pos_dict['z'] = '29idKappa:m4.VAL'
    pos_dict['th'] = '29idKappa:Euler_Theta'
    pos_dict['chi'] = '29idKappa:Euler_Chi'
    pos_dict['phi'] = '29idKappa:Euler_Phi'
    pos_dict['tth'] = '29idKappa:m9.VAL'
    pos_dict['kth'] = '29idKappa:m8.VAL'
    pos_dict['kappa'] = '29idKappa:m7.VAL'
    pos_dict['kphi'] = '29idKappa:m1.VAL'

    try:
        posname = (data[1].p[0].name)
        pos_start = round(data[1].p[0].data[0])
        pos_end = round(data[1].p[0].data[-1])
        pos_unit = data[1].p[0].unit
        scantype = list(pos_dict.keys())[list(pos_dict.values()).index(posname)]
        if scantype == 'tth':
            try:
                if data[1].p[2].name == '29idKappa:Euler_Chi':
                    scantype='hkl (tth)'
            except:
                scantype = 'tth'
    except:
        posname = 'none'
        pos_start = 'none'
        pos_end = 'none'
        pos_unit = 'none'
        scantype = 'Unknown scan'

    return scantype + ' scan ' + str(pos_start)+' - '+str(pos_end) + ' ' + pos_unit

def Kappa_scan_energy(scanNum,path,**kwargs):
    data = Kappa_get_data(scanNum,path,**kwargs)

    header = data[0]['29idmono:ENERGY_MON']
    
    return header[2][0]

def Kappa_scan_detail_list(scanNum,path,**kwargs):
    """
    returns spec string
    """
    data = Kappa_get_data(scanNum,path,**kwargs)

    sample_dict = {'x':'29idKappa:m2.RBV'}
    sample_dict['y'] = '29idKappa:m3.RBV'
    sample_dict['z'] = '29idKappa:m4.RBV'
    sample_dict['th'] = '29idKappa:Euler_ThetaRBV'
    sample_dict['chi'] = '29idKappa:Euler_ChiRBV'
    sample_dict['phi'] = '29idKappa:Euler_PhiRBV'
    sample_dict['tth'] = '29idKappa:m9.RBV'
    sample_dict['kth'] = '29idKappa:m8.RBV'
    sample_dict['kappa'] = '29idKappa:m7.RBV'
    sample_dict['kphi'] = '29idKappa:m1.RBV'
    sample_dict['energy'] = '29idmono:ENERGY_MON'
    sample_dict['TA'] = '29idd:LS331:TC1:SampleA'
    sample_dict['pol'] = 'ID29:ActualMode'
    energy  = data[0][sample_dict['energy']]
    TA = data[0][sample_dict['TA']]
    pol = data[0][sample_dict['pol']]

    try:
        return 'E({}): {:.1f} T(K): {:.1f} pol: {}'.format(energy[1],energy[2][0],TA[2][0],pol[2].split(',')[1])
    except:
        return 'E({}): {:.1f} T(K): {:.1f} pol: {}'.format(energy[1],energy[2][0],TA[2][0],pol[2])
