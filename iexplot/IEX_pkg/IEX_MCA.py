import os
import numpy as np

from iexplot.IEX_pkg.IEX_MDA import IEX_MDA
from iexplot.pynData import nstack
from iexplot.utilities import _create_dir_shortlist, take_closest_value


class IEX_MCA(IEX_MDA):
    """
    load IEX mca files and adds plotting methods
    mca files are of type scanH mda files
    
    usage: used by IEXdata or can be used alone 
        kwargs = {
            'prefix':'ARPES_',
            'nzeros':4,
            'suffix':'',
            'ext':"mda",
            'path':'/Users/jmcchesn/Documents/NoteBooks/Data/Brahlek/Brahlek_2021_2/mda/'
            }

        short_list=[127]
        data = IEX_MDA()

    """
    def __init__(self,**kwargs):
        """

        """
        self.prefix = ''
        self.nzeros = 4
        self.ext = 'mda'
        self.path = ''

        self._update_attr(**kwargs)

        pass

    def _update_attr(self, **kwargs):
        for key in kwargs:
            if key in vars(self):
                setattr(self,key,kwargs[key])
    
    def load(self,scan_list,image=True,**kwargs):
        """
        Loads mca spectra returns the data as
            2D pynData if image = True
            dictionary of 1D spectr if image = False
            
        """
        mda_d = self._load_1D_scans(scan_list,**kwargs)
        if image:
            return self._stack_1D_scans(mda_d)
        else:
            return mda_d
            
                
    def _load_1D_scans(self,scan_list,**kwargs):
        """
        uses IEX_MDA to load scans
        ** kwargs:
            path (default: self.path)
            prefix (default: self.prefix) 
            nzeros (default: self.nzeros)
            ext (default: self.ext)

        filename = prefix + scanNum.zfill(n) + suffix + "." + ext
        fpath = path + filename

        """
        kwargs.setdefault('debug',False)
        self._update_attr(**kwargs)
   

        if kwargs['debug']: 
            print('MCA path = ',self.path)

        d = IEX_MDA(path=self.path,prefix=self.prefix,ext=self.ext)
        mda_d = d.load_scans(scan_list)
        
        return mda_d
    
    def _stack_1D_scans(self,mda_d,**kwargs):
        """
        stacks all scans in dictionary of mda scans
        """
        self._update_attr(**kwargs)
        channels = list(mda_d.keys())
        nData_list = []
        for scanNum in channels:
            nData_list.append(mda_d[scanNum].det[1])
        stack = nstack(nData_list,stack_scale=channels,stack_unit='channels')
        return stack
    

