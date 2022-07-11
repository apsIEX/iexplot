#nADtiff.py 
#converts tiff data to a pynData object

__version__= 1.0      #JLM 6/27/2021

import re
import ast
import numpy as np
import tifffile

from iexplot.pynData.pynData import nData


def main():
    pass

                            
class nTiff:
    def __init__(self,*fpath,**kwargs):
        """
        fpath = full path including filename and extension
        
        kwargs:
            q = 1 (default); quiet if not 1 prints full file path when loading
            debug=False
        Usage: 
        tif=ntif(fpath)
        """
        kwargs.setdefault('q',1)
        kwargs.setdefault('debug',False)
        
        if kwargs['debug']:
            print('\nADtiff')
        
        self.fpath=''
        self.scanNum=None
        self.header={}
        
        if fpath:
            self.fpath=fpath[0]
            self._extractAll(**kwargs)
        else:
            pass
            
            
        def _extractAll(self, **kwargs):
            kwargs.setdefault('q',1)
            kwargs.setdefault('debug',False)
            
            data=tifffile.imread(fpath)
            tif=nData(data)
            return tif