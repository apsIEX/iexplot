import os

from iexplot.pynData.nEA import nEA

class IEX_EA():
    """

    """
    def __init__(self,**kwargs):
        """
        p = test if not None else None
        """
        self.dtype = None
        self.nzeros = None
        self.source = None
        self.center_channel = None
        self.first_channel = None
        self.deg_per_pixel = None
        self.crop_start = None
        self.crop_stop = None
        self.path = None

        if 'dtype' in kwargs:
            self.dtype = kwargs['dtype']
            self.set_by_dtype(self.dtype)
            self.path = kwargs['path']

        pass

    def set_by_dtype(self,dtype,**kwargs):
        """
        default variable for EA for IEX as fo 05/10/2021

        """
        kwargs.setdefault('debug',False)
        
        if kwargs['debug']:
            print('\nIEX_EA.set_bu_dtype')
            print('\t'+dtype)

        if dtype == "EA_nc":
            self.dtype = "nc"
            self.nzeros = 4
            self.source = "APS_IEX"
            self.center_channel = 571-50
            self.first_channel = 0#
            self.deg_per_pixel = 0.0292717
            self.crop_start = 338-50
            self.crop_stop = 819-50
        elif dtype == "EA":
            self.dtype = "h5"
            self.nzeros = 4
            self.source = "APS_IEX"
            self.center_channel = 571-50
            self.first_channel = 0
            self.deg_per_pixel = 0.0292717
            self.crop_start = 338-50
            self.crop_stop = 819-50
    
    def set_file_info(self,path,prefix,):
        self.path = path


    def load(self,shortlist,**kwargs):
        """
        returns a dictionary of loaded EA scans
        shortlist: list of EAscanNums to load
            
        **kwargs:
            path (default: self.path)
            prefix (default: self.prefix) 
            nzeros (default: self.nzeros)
            suffix (default: self.suffix)
            ext (default: self.ext)

            filename = prefix + scanNum.zfill(n) + suffix + "." + ext
            fpath = path + filename

            """
        kwargs.setdefault("debug",False) 

        d={}
                
        if kwargs["debug"]:
            print('\nIEX_EA.load')
        
        #create list of filename to load
        files2load = [kwargs['prefix']+str.zfill(str(x),kwargs['nzeros'])+kwargs['suffix']+"."+kwargs['ext'] for x in shortlist]
        if kwargs['debug']:
            print('\nfiles2load:',files2load)
        
        #load files and add to / update exp dictionary
        for (i,fname) in enumerate(files2load):
            ##### File info:
            fullpath=os.path.join(kwargs['path'],fname)
            if kwargs["debug"]:
                print("EA fullpath: ",fullpath)
            EA=nEA((fullpath),**kwargs)#nEA(fullpath,**kwargs)              
            d.update({shortlist[i]:EA})
        return d
        
